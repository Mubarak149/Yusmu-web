from django.urls import path
from .views import *

urlpatterns = [
    path("initiate-payment/", InitiatePayment.as_view(), name="initiate-payment"),
    path("callback-payment/", PaymentCallback.as_view(), name="callback-paymnet"),
    path("cancel-payment/", PaymentCancel.as_view(), name="payment-cancel"),
    path("payment-status/", PaymentStatus.as_view(), name="payment-success")
]
