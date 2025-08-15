import random
import string
from django.core.mail import send_mail
from django.conf import settings



def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits,k=6))


def send_otp_email(user,otp_code):
    """send otp email to user"""
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is:{otp_code}.This OTP is only valid for 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject,message,from_email,recipient_list)

    
