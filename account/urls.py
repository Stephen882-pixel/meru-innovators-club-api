from django.urls import path
from account.views import (ChangePasswordView, CustomTokenRefreshView, LogoutView, RegisterView,
                           LoginView, UserDataView,AllUsersView,RequestPasswordResetView,
                           ResetPasswordView,UserProfileUpdateView,DeleteAccountView,UnifiedOTPVerificationView)

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('token/refresh/',CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('get-user-data/',UserDataView.as_view(),name='get_user_data'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('get-all-users/',AllUsersView.as_view(),name='get_all_users'),
    path('password-reset/request/',RequestPasswordResetView.as_view(),name='request-password-reset'),
    path('password-reset/reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('update-user-profile/', UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('verify-otp/', UnifiedOTPVerificationView.as_view(), name='verify-otp'),
]
