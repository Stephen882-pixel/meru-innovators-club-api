import json
from datetime import timedelta
from http.client import responses
from unittest.mock import patch,MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import UserProfile,OTP,PasswordResetRequest,PasswordResetSession
from account.serializers import (
    RegisterSerializer,LoginSerializer,ChangePasswordSerializer,
    RequestPasswordResetSerializer,ResetPasswordSerializer
)

class BaseAuthTestCase(APITestCase):
    """Base test case  with common setup for authentication"""

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'password': 'TestPass123',
            'course': 'Computer Science'
        }

        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='TestPass123',
            is_active=True
        )

        # Create user profile
        self.test_profile = UserProfile.objects.create(
            user=self.test_user,
            course='Computer Science',
            registration_no='CS12345',
            bio='Test bio'
        )

        refresh = RefreshToken.for_user(self.test_user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def authenticate_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=F'Bearer {self.access_token}')


class RegisterViewTests(BaseAuthTestCase):
    """Test case for user registration"""
    def test_successful_registration(self):
        with patch('account.views.send_the_otp_email') as mock_send_otp:
            response = self.client.post(reverse('register'), self.user_data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['status'], 'success')
            self.assertIn('Account created successfully', response.data['message'])

            # Check user was created but inactive
            user = User.objects.get(username='johndoe')
            self.assertFalse(user.is_active)
            self.assertTrue(UserProfile.objects.filter(user=user).exists())
            self.assertTrue(OTP.objects.filter(user=user).exists())

            # Check OTP email was sent
            mock_send_otp.assert_called_once()

    def test_duplicate_username_registration(self):
        User.objects.create_user(username='johndoe',email='otherexample.com')

        response = self.client.post(reverse('register'), self.user_data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username already exists',response.data['message'])

    def test_duplicate_email_registration(self):
        User.objects.create_user(username='othername', email='john.doe@example.com')

        response = self.client.post(reverse('register'), self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', response.data['message'])

    def test_invalid_password_registration(self):
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'weak'

        response = self.client.post(reverse('register'),invalid_data)

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors',response.data)


    def test_missing_fields_registration(self):
        incomplete_data = {'email': 'test@example.com', 'password': 'TestPass123'}

        response = self.client.post(reverse('register'), incomplete_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




