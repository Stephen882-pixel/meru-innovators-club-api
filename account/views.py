from tokenize import TokenError
from venv import logger
import logging
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination

from account.models import PasswordResetRequest
from .serializers import RegisterSerializer, LoginSerializer,ChangePasswordSerializer,status
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from account import serializers
from django.db import IntegrityError

import secrets
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from.models import UserProfile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.exceptions import ValidationError


# Create your views here.
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


import jwt
from rest_framework import status
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenRefreshView
import traceback
from datetime import timedelta
from Innovation_WebApp.Email import send_the_otp_email
import random
import string

from django.db.models import Prefetch


class RegisterView(APIView):

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Register a new user and send an OTP to their email for verification.",
        request_body=RegisterSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Account created successfully. OTP sent to email.",
                examples={
                    "application/json": {
                        "message": "Account created successfully. Please check your email for OTP verification code.",
                        "status": "success",
                        "user_data": None
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Validation error or duplicate email/email.",
                examples={
                    "application/json": {
                        "message": "Username already exists. Please choose a different username.",
                        "status": "failed",
                        "errors": {"username":"Username already exists"},
                        "data": None
                    }
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Unexpected server error",
                examples= {
                    "application/json": {
                        "message": "An unexpected error occured...",
                        "status": "failed",
                        "data": None
                    }
                }
            ),
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                

                try:
                    otp_code = ''.join(random.choices('0123456789', k=6))
                    otp = OTP.objects.create(
                        user=user,
                        otp_code=otp_code,
                    )
                    send_the_otp_email(user,otp)
                except Exception as e:
                    return Response({
                        "message": f'Failed to send OTP email: {str(e)}',
                        "status": "failed",
                        "data": None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    "message": "Account created successfully. Please check your email for OTP verification code",
                    "status": "success",
                    "user_data": None
                }, status=status.HTTP_201_CREATED)
                
            except IntegrityError as e:
                if "username" in str(e).lower():
                    return Response({
                        "message": "Username already exists. Please choose a different username.",
                        "status": "failed",
                        "errors": {"username": "Username already exists"},
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif "email" in str(e).lower():
                    return Response({
                        "message": "Email already exists. Please use a different email or try logging in.",
                        "status": "failed",
                        "errors": {"email": "Email already exists"},
                        "data": None
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "message": f"Database error: {str(e)}",
                        "status": "failed",
                        "data": None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "message": f"An unexpected error occurred: {str(e)}",
                    "status": "failed",
                    "data": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        error_details = {}
        for field, errors in serializer.errors.items():
            error_details[field] = str(errors[0]) if errors else "Invalid data"

        if "username" in error_details and "already exists" in error_details["username"].lower():
            message = "Username already exists. Please choose a different username."
        elif "email" in error_details and "already exists" in error_details["email"].lower():
            message = "Email already exists. Please use a different email or try logging in."
        else:
            message = "There was a problem signing up. Please check the details and try again."
            
        return Response({
            "message": message,
            "status": "failed",
            "errors": error_details,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    


class UnifiedOTPVerificationView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response({
                "message": "Email and OTP are required",
                "status": "error",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find the user
        try:
            user = User.objects.get(email=email)
            # Auto-detect verification type based on user's active status
            verification_type = 'registration' if not user.is_active else 'password_reset'
            
        except User.DoesNotExist:
            return Response({
                "message": "User not found",
                "status": "error",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get and verify OTP
        try:
            # Get the most recent unverified OTP for the user
            otp_obj = OTP.objects.filter(
                user=user,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not otp_obj:
                return Response({
                    'message': 'No OTP found for this account. Please request a new OTP',
                    'status': 'error',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Check if OTP is valid and matches
            if not otp_obj.is_valid():
                return Response({
                    'message': 'OTP has expired. Please request a new one',
                    'status': 'error',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_code != otp_obj.otp_code:
                return Response({
                    'message': 'Invalid OTP',
                    'status': 'error',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as verified
            otp_obj.is_verified = True
            otp_obj.save()
            
            # For registration: activate the user account
            if verification_type == 'registration':
                user.is_active = True
                user.save()
                return Response({
                    "message": "Email verified successfully. You can now login",
                    "status": 'success',
                    "data": None
                }, status=status.HTTP_200_OK)
            # For password reset: just confirm OTP verification
            else:
                return Response({
                    "message": "OTP verified successfully. You can now reset your password",
                    "status": 'success',
                    "data": None
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'message': f'An error occurred: {str(e)}',
                'status': 'error',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Authenticate a user and return JWT access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Login Successfull",
                examples={
                    "application/json": {
                        "message": "Login successfully",
                        "status": "success",
                        "data": {
                            "refresh":"eyJ0eXAiOiJKV1QiLCJh...",
                            "access": "eyJ0eXAiOiJKV1QiLCJh..."
                        }
                    }
                }
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description="Invalide credentials or email not verified",
                examples={
                    "application/json": {
                        "message": "Email not verified. Please verify your email.",
                        "status": "error",
                        "data": None
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Validation errors",
                examples={
                    "application/json":{
                        "email":["This field is required"],
                        "password":["This fields is required"]
                    }
                }
            )
        }
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(
                data=request.data, 
                context={'request': request}
            )
            
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            # check if the user is verified
            if not user.is_active:
                return Response({
                    'message':'Email not verified.Please verify your email.',
                    'status':'error',
                    'data':None
                },status=status.HTTP_403_FORBIDDEN)
            
            tokens = self.get_tokens_for_user(user)
            
            return Response({
                'message':'Login successfull',
                'status': 'success',
                'data':tokens
                
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': f'Login processing failed',
                'status': serializer.errors,
                'data':None
            }, status=status.HTTP_403_FORBIDDEN)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
class LogoutView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="Logs out the user by blacklisting the provided refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh_token"],
            properties={
                "refresh_token":openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The refresh token issued at login."
                ),
            },
            example={
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Logout successfully",
                examples={
                    "application/json": {
                        "message": "logout successfully",
                        "status":"success",
                        "data": None
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Invalid or missing refresh tokens",
                examples={
                    "application/json": {
                        "message":"Invalid or expired refresh token",
                        "status":"error",
                        "data": None
                    }
                }
            )
        }
    )
    def post(self,request):
        try:
            # Get the refresh tokens from the request body
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    "message":"Refrersh token is required",
                    "status":"error",
                    "data":None
                },status=status.HTTP_400_BAD_REQUEST)
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message":"Logout successful",
                "status":"success",
                "data":None
            },status=status.HTTP_200_OK)
        except TokenError:
            return Response({
                "message":"Invalid or expired refresh token",
                "status":"error",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            return Response({
                "message":f"Logout failed: {str(e)}",
                "status":"error",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
            



from django.core.signing import TimestampSigner,BadSignature
import uuid


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_description="""
        Change the password of the currently logged-in user.  
        - Requires **Bearer token authentication**.  
        - New password must meet strength requirements:
            * At least 8 characters  
            * At least one uppercase letter  
            * At least one lowercase letter  
            * At least one number  
            * At least one special character
        """,
        request_body=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Password change request created successfully. Email verification required.",
                examples={
                    "application/json":{
                        "message":"Please check your email to verify this request",
                        "status":"pending",
                        "data":None
                    }
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Validation error",
                examples={
                    "application/json":{
                        "old_password": "Current password is incorrect",
                        "new_password": "New password must be at least 8 characters long"
                    }
                }
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json":{
                        "detail": "Authentication credentials were not provided."
                    }
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Unexpected server error",
                examples={
                    "application/json":{
                        "message":"Unexpected error occured",
                        "status":"failed",
                        "data": None,
                        "detail":"Detailed error message"
                    }
                }
            )
        }
    )
    def post(self,request):
        try:
            user = request.user
            token = generate_verification_token_for_password_reset(user)
            change_request = PasswordResetRequest.objects.create(
                user=user,
                token=token,
                old_password=request.data.get('old_password'),
                new_password=request.data.get('new_password'),
                expires_at=timezone.now() + timedelta(hours=1)
            )
            print(f"Created PasswordChangeRequest:{change_request}")
            send_password_change_email(user,token)
            return Response({
                'message':'Please check your email to verify this request',
                'status':'Pending',
                'data':None
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':'Unexpected erro occured',
                'status':'failed',
                'data':None,
                'detail':str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class VerifyPasswordChangeView(APIView):
    permission_classes = []
    serializer_class = ChangePasswordSerializer


    def get(self, request,token):
        try:
            # verify token
            signer = TimestampSigner()
            print(f"Received token: {token}")
            unsigned_value = signer.unsign(token,max_age=3600) # has a one our expiry
            print(f"Unasigned value:{unsigned_value}")
            user_id = int(unsigned_value.split(':')[0])
            print(f"Extracted user_id:{user_id}")
            user = User.objects.get(id=user_id)

            # check database
            change_request = PasswordResetRequest.objects.get(token=token,user_id=user_id)
            print(f"Found change_request: user = {change_request,user_id},token={change_request.token},expires at={change_request.expires_at}")

            if change_request.is_expired():
                print(f"Request expired: current_time={timezone.now()},expires_at={change_request.expires_at}")
                change_request.delete()
                return Response({
                    'message':'Password change session expired',
                    'status':'failed',
                    'data':None
                },status=status.HTTP_400_BAD_REQUEST)
            
            # procced with change password
            password_data = {
                "old_password":change_request.old_password,
                "new_password":change_request.new_password,
                "confirm_password":change_request.new_password
            }

            serializer = self.serializer_class(
                data=password_data,
                context={'request':request,'user':change_request.user}
            )
            if serializer.is_valid():
                serializer.save()
                change_request.delete()
                return Response({
                    'message':'Password changed succefully',
                    'status':'success',
                    'data':None
                },status=status.HTTP_200_OK)
            return Response({
                'message':'An error occured,please try again',
                'status':'failed',
                'errors':serializer.errors,
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            print(f"BadSignature:Token {token} is invalid or tempered")
            return Response({
                'message':'Invalid or expired verification token',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
        except PasswordResetRequest.DoesNotExist:
            print(f"No PasswordChangeRequest found for token : {token},user_id:{user_id}")
            return Response({
                'message':'Password change session expired',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
        except (BadSignature,User.DoesNotExist,ValueError):
            return Response({
                'message':'Invalid or expired verification token',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({
                'mesage':'An unexpected error occured',
                'status':'failed',
                'data':None
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        
import json
class UserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # Get the authenticated user
        user = request.user
        try:
            # fetch user profile details
            user_profile = UserProfile.objects.get(user=user)

            # Return comprehensive user data
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'course': user_profile.course,
                # Include all the additional fields
                'registration_no': user_profile.registration_no,
                'bio': user_profile.bio,
                'tech_stacks': json.loads(user_profile.tech_stacks) if user_profile.tech_stacks else [],
                'social_media': json.loads(user_profile.social_media) if user_profile.social_media else {},
                'photo': request.build_absolute_uri(user_profile.photo.url) if user_profile.photo else None,
                #'year_of_study': user_profile.year_of_study,
                'graduation_year': user_profile.graduation_year,
                'projects': json.loads(user_profile.projects) if user_profile.projects else [],
                'skills': json.loads(user_profile.skills) if user_profile.skills else []
            }

            return Response({
                'message':'User data retrieved successfully',
                'status':'success',
                'data':user_data
            },status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                'error':'User profile does not exist'
            },status=status.HTTP_404_NOT_FOUND)
        

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """Get detailed user profile data"""
        user = request.user
        try:
            user_profile = UserProfile.objects.get(user=user)

            # Prepare the response with all available user data
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'course': user_profile.course,
                'registration_no': user_profile.registration_no,
                'bio': user_profile.bio,
                'tech_stacks': user_profile.get_tech_stacks(),
                'social_media': user_profile.get_social_media(),
                'photo': request.build_absolute_uri(user_profile.photo.url) if user_profile.photo else None,
                'year_of_study': user_profile.year_of_study,
                'graduation_year': user_profile.graduation_year,
                'projects': user_profile.get_projects(),
                'skills': user_profile.get_skills()
            }
            return Response({
                "message":"User Profile data retrieved successfully",
                "status":"success",
                "data":None
            },status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                "error":"User profile does not exist"
            },status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request):
        """update user profile data"""
        user = request.user
        try:
            user_profile = UserProfile.objects.get(user=user)

            # Update User model fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()


            # Update UserProfile fields
            if 'course' in request.data:
                user_profile.course = request.data['course']
            if 'registration_no' in request.data:
                user_profile.registration_no = request.data['registration_no']
            if 'bio' in request.data:
                user_profile.bio = request.data['bio']
            if 'tech_stacks' in request.data:
                user_profile.set_tech_stacks(request.data['tech_stacks'])
            if 'social_media' in request.data:
                user_profile.set_social_media(request.data['social_media'])
            if 'photo' in request.FILES:
                user_profile.photo = request.FILES['photo']
            if 'year_of_study' in request.data:
                user_profile.year_of_study = request.data['year_of_study']
            if 'graduation_year' in request.data:
                user_profile.graduation_year = request.data['graduation_year']
            if 'projects' in request.data:
                user_profile.set_projects(request.data['projects'])
            if 'skills' in request.data:
                user_profile.set_skills(request.data['skills'])
                
            user_profile.save()

            # Return updated user data
            updated_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'course': user_profile.course,
                'registration_no': user_profile.registration_no,
                'bio': user_profile.bio,
                'tech_stacks': user_profile.get_tech_stacks(),
                'social_media': user_profile.get_social_media(),
                'photo': request.build_absolute_uri(user_profile.photo.url) if user_profile.photo else None,
                'year_of_study': user_profile.year_of_study,
                'graduation_year': user_profile.graduation_year,
                'projects': user_profile.get_projects(),
                'skills': user_profile.get_skills()
            }

            return Response({
                "message":"User profile updated successfully",
                "status":"success",
                "data":updated_data
            },status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                "error":"User profile does not exist"
            },status=status.HTTP_404_NOT_FOUND)
    def patch(self,request):
        """Partial update of user profile (same functionality as PUT for this case)"""
        return self.put(request)
    


class VerifyEmailView(APIView):
    def get(self,request):
        uid =request.GET.get('uid')
        token = request.GET.get('token')

        try:
            # Decode user ID
            user_id = urlsafe_base64_encode(uid).decode()
            user = User.objects.get(pk=user_id)

            # Check token validity
            if default_token_generator.check_token(user,token):
                user.is_active = True
                user.save()
                return Response({
                    'message':'Emale verified successfully.You can now login'
                },status=status.HTTP_200_OK)
            else:
                return Response({
                    'message':'Invalide or expired Token'
                },status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist,ValueError,TypeError):
            return Response({
                'message':'Invalide token or user ID'
            },status=status.HTTP_400_BAD_REQUEST)
        
class EmailVerificationView(APIView):
    def get(self,request,token):
        try:
            # Decode the token (you can replace this with your actual token validation)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])

            # Mark user as active
            user.is_active =  True
            user.save()


            return HttpResponse("Email verified successfully!", status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return HttpResponse("Verification token has expired", status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return HttpResponse("Invalid token", status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    def post(self,request,*args,**kwargs):
        try:
            old_refresh_token = RefreshToken(request.data['refresh'])
            user = User.objects.get(id=old_refresh_token['user_id'])
            new_refresh = RefreshToken.for_user(user)
            new_refresh = RefreshToken.for_user(user)
            return Response({
                'message':'User logged in',
                'status':'success',
                'data':{
                    'access':str(new_refresh.access_token),
                    'refresh':str(new_refresh)
                }
            },status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error:{str(e)}")
            print(traceback.format_exc())
            return Response({
                'message':'User not logged in',
                'status':'error',
                'data':None
            },status=status.HTTP_401_UNAUTHORIZED)
        

class UsersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Retrieve all users in thee database
class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            # get all users with prefeched profiles
            users = User.objects.all().prefetch_related(
                Prefetch('userprofile',queryset=UserProfile.objects.all(),to_attr='profile')
            )

            # Initialize pagination
            paginator = UsersPagination()

            # paginate the querryset

            page = paginator.paginate_queryset(users,request)

            # process the paginated users
            user_data_list = []
            for user in page:
                # Check if profile exists using the prefetched data
                profile = user.profile_cache[0] if hasattr(user,'profile_cache') and user.profile_cache else None

                user_data = {
                    'id':user.id,
                    'username':user.username,
                    'email':user.email,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'course':profile.course if  profile else None,
                    'photo':request.build_absolute_uri(profile.photo.url) if profile and profile.photo else None,
                }
                user_data_list.append(user_data)

            # Return paginated response
            return Response({
                'message':'All users retrieved successfully',
                'status':'success',
                'data':{
                    'count': paginator.page.paginator.count,  # Total count from paginator
                    'next':paginator.get_next_link(),
                    'previous':paginator.get_previous_link(),
                    'results':user_data_list
                }
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error':f'error fetching users:{str(e)}'
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializers import UserSerializer  # Ensure you have a UserSerializer

User = get_user_model()

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Require authentication to access
def get_all_users(request):
    users = User.objects.all()  # Get all users
    serializer = UserSerializer(users, many=True)  # Serialize users
    return Response(serializer.data, status=status.HTTP_200_OK)



# forgot password view

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import OTP,PasswordResetSession
from .serializers import RequestPasswordResetSerializer,VerifyOTPSerializer,ResetPasswordSerializer
from .utils import generate_otp,send_otp_email
from django.utils import timezone
from rest_framework.authtoken.models import Token

class RequestPasswordResetView(APIView):
    def post(self,request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)


            # Invalidate any existing OTPs for this user
            OTP.objects.filter(user=user,is_verified=False).update(expires_at=timezone.now())


            # Generate and save a neww otp
            otp_code = generate_otp()
            OTP.objects.create(user=user,otp_code=otp_code)


            # Send otp email
            send_otp_email(user,otp_code)


            return Response({"message":"OTP has been sent to your email."},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']

            user = User.objects.get(email=email)
            # Check for a recently verified OTP
            otp = OTP.objects.filter(
                user=user,
                is_verified=True  # Assumes OTP was marked verified in VerifyOTPView
            ).order_by('-created_at').first()

            if otp and otp.is_valid():  # Ensure OTP is still valid (not expired)
                user.set_password(new_password)
                user.save()
                otp.delete()  # Clean up the OTP after use
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            return Response({"message": "No valid verified OTP found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# google oauth 
User = get_user_model()

# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])  # Ensure authentication is required
# def get_all_users(request):
#     try:
#         users = User.objects.all()  # Get all users
        
#         # Initialize the pagination class
#         paginator = UsersPagination()
        
#         # Paginate the queryset
#         paginated_users = paginator.paginate_queryset(users, request)
        
#         # Serialize the paginated data
#         serializer = UserSerializer(paginated_users, many=True)
        
#         # Return the paginated response
#         return paginator.get_paginated_ressponse(serializer.data)
#     except Exception as e:
#         print(f"Pagination error: {str(e)}")
#         # Fallback to non-paginated response
#         serializer = UserSerializer(users, many=True)
#         return Response({
#             'message': 'All users retrieved successully',
#             'status': 'success',
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Delete the authenticated user's account
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


