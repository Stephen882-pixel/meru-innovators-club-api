from django.urls import path
from django.contrib import admin
from account.views import (ChangePasswordView, CustomTokenRefreshView, LogoutView, RegisterView,
                           LoginView, UserDataView,VerifyEmailView,EmailVerificationView,AllUsersView,ResendOTPView,
                           VerifyPasswordChangeView,RequestPasswordResetView,ResetPasswordView,UserProfileUpdateView)
from .views import DeleteAccountView, UnifiedOTPVerificationView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from .views import get_all_users

urlpatterns = [
    # Authentication Routes
    path('register/',RegisterView.as_view(),name='register'),
    #path('verify-otp/', VerifyRegisterOTPView.as_view(), name='verify-otp'),
    #path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('verify-email/<str:token>', EmailVerificationView.as_view(), name='verify_email'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),

    # Authentication Routes
    path('logout/', LogoutView.as_view(), name='logout'),
   

    # Endpoint to verify and complete password change (GET request)
    path('verify-password-change/<str:token>/',VerifyPasswordChangeView.as_view(),name='verify-password-change'),
    # Endpoint to initiate password change (POST request)
     path('change-password/', ChangePasswordView.as_view(), name='change_password'),
  

    # JWT Token Routes
    path('token/refresh/',CustomTokenRefreshView.as_view(), name='token_refresh'),
    #path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    

    # get user data with access tokens
    path('get-user-data/',UserDataView.as_view(),name='get_user_data'),
    
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),


    # retrieve all users from the database
    path('get-all-users/',AllUsersView.as_view(),name='get_all_users'),

    # forgot password
    path('password-reset/request/',RequestPasswordResetView.as_view(),name='request-password-reset'),
    #path('password-reset/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset/reset/', ResetPasswordView.as_view(), name='reset-password'),

    # update user data
    path('update-user-profile/', UserProfileUpdateView.as_view(), name='user_profile_update'),


    path('verify-otp/', UnifiedOTPVerificationView.as_view(), name='verify-otp'),
   
]