
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .tasks import sent_email_to
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


import requests

# Create your views here.

class SignupView(APIView):
    def post(self, request):
        serializers = UsermodelSignupSerializer(data = request.data)
        if serializers.is_valid():
            user = serializers.save()
            otp = str(random.randint(100000, 999999))
            subject = 'Verification'
            plain_message = f"your otp is {otp}"
            sent_email_to.delay(email= user['email'], text = plain_message, subject=subject)
            user = CustomUser.objects.get(email = serializers.data["email"])
            user.otp = otp
            user.save()
            return Response({ "success": True, "message": "user create successfully!", "data":serializers.data, "verify_url": f"http://127.0.0.1:8000/auth/verify/{user.username}/"},status=status.HTTP_201_CREATED)

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Verify_Email_Signup(APIView):
    def post(self,request, username):
        serializers = OTPSerializer(data = request.data)
        if serializers.is_valid():
            try:
                user = CustomUser.objects.get(username = username)
                otp = user.otp
                if serializers.data['otp'] == otp:
                    user.is_email_varified = True
                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    return Response({"message":"verifyed successfully"}, status = status.HTTP_200_OK)
                else:
                    return Response({"message":"wrong varification code!"})

            except CustomUser.DoesNotExist:
                return Response({"message":"user not found"})

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self,request):
        serializer = LoginSerializers(data = request.data)
        if serializer.is_valid():
            user = authenticate(username = serializer.data['username'], password = serializer.data['password'])
            if user:
                if user.is_email_varified:
                    refresh = RefreshToken.for_user(user)
                    return Response( {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                
                otp = str(random.randint(100000, 999999))
                subject = 'Verification'
                plain_message = f"your otp is {otp}"
                sent_email_to.delay(email= user.email, text = plain_message, subject=subject)
                user.otp = otp
                user.save()
                return Response(
                    {
                        "message":"we sent a otp to your email!", 
                        "url":f"http://127.0.0.1:8000/auth/verify/{user.username}/"
                        }
                    )
            
            return Response({"message":"username or password Invalid! or email is not varified!"}, status=status.HTTP_400_BAD_REQUEST)   
        return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user        
        serializer =  ChangePassword_serializer(data = request.data)
        if serializer.is_valid():
            hash_password = user.password
            raw_password = serializer.data['old_password']
            if check_password(raw_password, hash_password):
                user.set_password(serializer.data['new_password'])
                user.save()
                return Response({"message":"Password changed successfully!"}, status= status.HTTP_200_OK)
            else:
                return Response({"message":"worng old password!"}, status=status.HTTP_400_BAD_REQUEST )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class FogetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(username = serializer.data['username'])
                otp = str(random.randint(000000, 999999))
                user.otp = otp
                user.save()
                subject = 'Verification'
                plain_message = f"your otp is {otp}"
                sent_email_to.delay(email= user.email, text = plain_message, subject=subject)
                return Response(
                    {
                    "message":"Enter your username parform a post method!",
                    "varify_url": f"http://127.0.0.1:8000/auth/vefiry_for_forget/{user.username}/"
                    },
                    status=status.HTTP_200_OK
                    )
            except CustomUser.DoesNotExist:
                return Response({"message":"user not found!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        

class Verify_User_ForgetPassword(APIView):
    def post(self, request, username):
        serializer = OTPSerializer(data = request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(username = username)
                otp = user.otp
                if serializer.data['otp'] == otp:
                    refresh = RefreshToken.for_user(user)
                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    return Response( {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"wrong varification code!"})

            except CustomUser.DoesNotExist:
                return Response({"message":"user not found"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({ "success": True, "message": "password reset successfully", "data": None }, status=status.HTTP_200_OK)
        return Response({ "success": False, "message": "validation error!", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)





def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        print(token)    
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get("email")
            owner_name = idinfo.get("name")
            

            users, created = CustomUser.objects.get_or_create(email=email)
            users.owner_name=owner_name
            users.defaults={"email": email}
            users.is_email_verified=True
            # if multiple user have to define user type
            users.save()

            return Response(generate_tokens_for_user(users), status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
