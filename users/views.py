from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
#rest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework.exceptions import AuthenticationFailed



class LoginView(APIView):
    # API View to handle user login requests
    def post(self, request, *args, **kwargs):
        # Deserialize and validate the incoming request data
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            # Authenticate the user using Django's built-in authentication system
            user = authenticate(username=username, password=password)
            if user is not None:
                # Log in the user and establish a session
                login(request, user)
                if user.user_type == "3": # user type 3 is a student
                    # return redirect('dashboard')  # Replace 'dashboard' with your actual URL name or path
                    # Redirect to the user's dashboard or detail page with their ID
                    return redirect(reverse('dashboard'))
                elif user.user_type == "2":  # user type 2 is a teacher
                    return Response(
                        {"Message":"LoginSuccess"}, status=status.HTTP_200_OK)
                elif user.user_type == "1":  # user type 1 is a admin
                    pass
            # Raise an error if authentication fails
            raise AuthenticationFailed("Invalid username or password")
        # Return validation errors if input data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data.get('username')
#             password = serializer.validated_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 if not user.is_active:
#                     raise AuthenticationFailed("User account is inactive.")
#                 login(request, user)
#                 return Response(
#                     {
#                         "message": "Login successful",
#                         "user_type": user.user_type,
#                         "username": user.username,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             raise AuthenticationFailed("Invalid username or password.")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    # API View to handle user logout requests
    def post(self, request, *args, **kwargs):
        # Log out the user and clear the session
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

