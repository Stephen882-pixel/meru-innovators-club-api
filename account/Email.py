from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_the_otp_email(user, otp):
    otp_details = {
        'user': user.first_name,
        'otp': otp.otp_code
    }
    subject = 'Verify Your Email Address'
    html_message = render_to_string('OTP/otp.html', {'otp_details': otp_details})
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        'ondeyostephen0@gmail.com',

        [user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
