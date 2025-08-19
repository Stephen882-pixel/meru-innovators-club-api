import re
from venv import logger
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
import logging
from.models import UserProfile
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password



User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=50)
    lastname = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)
    #registration_no = serializers.CharField(max_length=50)
    course = serializers.CharField(max_length=50)

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError("Invalid username format")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value
    
    def validate_course(self,value):
        if value.isspace():
            raise serializers.ValidationError("Please provide your course")
        
        return value

    def validate(self, data):
        username = data['username'].lower()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "Username already exists"})

        if User.objects.filter(email__iexact=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        return data
    
    def create(self, validated_data):
        course = validated_data.pop('course')
        with transaction.atomic():
            # Create User with 'is_active=False'
            user = User.objects.create_user(
                username=validated_data['username'].lower(),
                email=validated_data['email'],
                first_name=validated_data['firstname'],
                last_name=validated_data['lastname'],
                password=validated_data['password'],
                is_active=False, # User will remain inactive until the email is verified 
            )
            UserProfile.objects.create(
                user=user,
                course=course
            )
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
             user = User.objects.get(email=email)
             if not user.check_password(password):
                  raise serializers.ValidationError("Invalid credentials")

             if not user.is_active:
                  raise serializers.ValidationError("Account is disabled")

             data['user'] = user
             return data

        except User.DoesNotExist:
         raise serializers.ValidationError("Invalid credentials")
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
            
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
            
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
            
        return value

    def validate(self, data):
        user = self.context.get('user') or 'user' not in self.context
        if not user.is_authenticated and 'user' not in self.context:    
            raise serializers.ValidationError({
                "detail": "Authentication required"
            })
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                "old_password": "Current password is incorrect"
            })
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "New passwords do not match"
            })
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                "new_password": "New password must be different from current password"
            })

        return data

    def save(self, **kwargs):
        user = self.context.get('user') or self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exists")
        return value
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6,min_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
