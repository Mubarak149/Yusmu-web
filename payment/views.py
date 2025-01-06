import requests
import hmac
import hashlib
import uuid
import time
import json
import logging
import asyncio
import aiohttp
from asgiref.sync import sync_to_async, async_to_sync
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from .models import Payment
from student.models import StudentCourses




class OPayClient:
    def __init__(self, secret_key, merchant_id):
        self.secret_key = secret_key
        self.merchant_id = merchant_id

    def generate_signature(self, payload):
        # Serialize payload with consistent separators
        request_body = json.dumps(payload, separators=(',', ':'))
        # Generate HMAC SHA-512 signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            request_body.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        return signature

    def fetch_payment_status(self, url, country, reference):
        # Define the payload
        payload = {
            "country": country,
            "reference": reference,
        }

        # Generate the signature
        signature = self.generate_signature(payload)

        # Set headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {signature}',
            'MerchantId': self.merchant_id
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            # Process the response
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "Failed to fetch payment status",
                    "status_code": response.status_code
                }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

class PaymentRateThrottle(UserRateThrottle):
    rate = '5/minute'  # Limit to 5 payment attempts per minute

class InitiatePayment(APIView):
    logger = logging.getLogger('payment')
    """Handles payment initiation through OPay payment gateway."""
    throttle_classes = [PaymentRateThrottle]
    
    def post(self, request, *args, **kwargs):
        print("post met")
        return async_to_sync(self.async_post)(request, *args, **kwargs)
    
    def generate_reference(self):
        """Generate unique payment reference."""
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"{timestamp}-{unique_id}"

    def create_payment_data(self, request_data, reference, course_id):
        """Create standardized payment request data."""
        return {
            "country": "NG",
            "reference": reference,
            "amount": {
                "total": request_data['amount'],
                "currency": "NGN"
            },
            "returnUrl": f"{settings.BASE_URL}/client/payment-status/?reference={reference}&id={course_id}",
            "callbackUrl": f"{settings.BASE_URL}/client/callback-payment/",
            "cancelUrl": f"{settings.BASE_URL}/client/cancel-payment/",
            "displayName": settings.MERCHANT_DISPLAY_NAME,
            "expireAt": 300,
            "userInfo":{
                    "userEmail":"test@email.com",
                    "userId":"userid001",
                    "userMobile":"+23488889999",
                    "userName":"David"
            },
            "product": {
                "description": request_data['product_description'],
                "name": request_data['product_name']
            },
            "payMethod": "BankCard"
        }

    async def async_create_payment(self, url, payment_data, headers):
        print("first Run")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payment_data, headers=headers) as response:
                return await response.json()
     
    async def async_post(self, request, *args, **kwargs):
        try:
            self.logger.info(f"Payment initiation started for user: {request.user}")
            reference = self.generate_reference()
            payment_data = self.create_payment_data(
                request.POST,
                reference,
                request.POST['id']
            )

            headers = {
                'Authorization': f'Bearer {settings.OPAY_PUBLIC_KEY}',
                'MerchantId': settings.OPAY_MERCHANT_ID
            }

            # Call the async_create_payment method
            t1 = asyncio.create_task(self.async_create_payment(
                settings.OPAY_CASHIER_URL,
                payment_data,
                headers
            ))
            t2 = asyncio.create_task(self.count(
                settings.OPAY_CASHIER_URL,
                payment_data,
                headers
            ))
            tasks = [t1,t2]
            response_data = await asyncio.gather(*tasks)

            # Debugging: log response data
            print("Payment gateway response:", response_data)

            # Extract the cashierUrl from the response
            cashier_url = response_data.get("data", {}).get("cashierUrl")
            if not cashier_url:
                raise ValueError("No redirect URL found in response")

            return JsonResponse({'redirect_url': cashier_url})

        except aiohttp.ClientError as e:
            self.logger.error(f"Payment service unavailable: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'Payment service unavailable',
                'details': str(e)
            }, status=503)
        except ValueError as e:
            self.logger.error(f"Invalid response from payment service: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'Invalid response from payment service',
                'details': str(e)
            }, status=400)
        except Exception as e:
            self.logger.error(f"Payment failed: {str(e)}", exc_info=True)
            return JsonResponse({
                'error': 'Payment initiation failed',
                'details': str(e)
            }, status=500)
        
    
    

class PaymentStatus(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Extract parameters and validate
            reference, course = self._validate_request(request)
            if isinstance(course, Response):
                return course  # If validation returns a Response, return it directly
            
            # Fetch payment status
            response = self._fetch_payment_status(reference)
            if "error" in response:
                return Response(
                    {"error": response.get("error"), "status_code": response.get("status_code", 500)},
                    status=response.get("status_code", 500)
                )

            # Handle payment status
            return self._handle_payment_status(course, response)

        except KeyError as e:
            return Response({"error": f"Configuration key missing: {str(e)}"}, status=500)
        except requests.exceptions.RequestException as e:
            return Response({"error": "Network error occurred", "details": str(e)}, status=503)
        except Exception as e:
             return Response({"error": "An unexpected error occurred", "details": str(e)}, status=500)

    def _validate_request(self, request):
        """
        Validates the incoming request and retrieves course information.
        """
        reference = request.GET.get('reference', '').strip()
        course_id = request.GET.get('id', '')

        if not reference:
            return Response({"error": "No reference provided"}, status=400)

        try:
            course = StudentCourses.objects.get(id=course_id)
        except StudentCourses.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        return reference, course

    def _fetch_payment_status(self, reference):
        """
        Makes the API call to fetch the payment status.
        """
        country = "NG"
        url = "https://testapi.opaycheckout.com/api/v1/international/cashier/status"
        secret_key = settings.OPAY_API_SECRET_KEY
        merchant_id = settings.OPAY_MERCHANT_ID

        opay_client = OPayClient(secret_key, merchant_id)
        return opay_client.fetch_payment_status(url, country, reference)

    @transaction.atomic
    def _handle_payment_status(self, course, response):
        """
        Handles the payment status response and updates course enrollment if necessary.
        """
        payment_status = response.get("data", {}).get("status")
        if payment_status == "SUCCESS":
            # Create payment record
            # payment = Payment.objects.create(
            #     amount=response['data']['amount'],
            #     reference=response['data']['reference']
            # )
            print("payment success")
            return Response({"message": "Payment successful", "details": response}, status=200)
        elif payment_status == "PENDING":
            return Response({"message": "Payment is pending", "details": response}, status=200)
        elif payment_status == "INITIAL":
            return Response({"message": "Payment is in the initial state. Awaiting further processing.", "details": response}, status=200)
        else:
            failure_reason = response.get("data", {}).get("failureReason", "Unknown reason")
            return Response(
                {"message": f"Payment failed or closed: {payment_status}", "reason": failure_reason, "details": response},
                status=400
            )

class PaymentCallback(APIView):
    def get(self, request,*args,**kwargs):
        print('From opay callback')
        print(request.GET)
        data = request.GET
        return Response(data)
    
    def post(self, request,*args,**kwargs):
        print('opay call back')
        print(request.POST)
        data = request.POST
        return Response(data)
        
class PaymentCancel(APIView):
    def get(self, request,*args,**kwargs):
        print('This Bastard Cancel the Payment')
        print(request.GET)
        data = request.GET
        return Response(data)
    
    def post(self, request,*args,**kwargs):
        print('This Bastard Cancel the Payment')
        data = request.POST
        return Response(data)