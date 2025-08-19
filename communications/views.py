from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views, status
from .models import SubscribedUsers
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework.response import Response
import logging
logger = logging.getLogger(__name__)



class NewsletterSendView(views.APIView):
    @swagger_auto_schema(
        tags=["Newsletters"],
        operation_summary="Send newsletter emails to all subscribers",
        operation_description="""
            Sends a newsletter email to all subscribed users.  
            - Requires `subject` and `message` in the request body.  
            - Authenticated user’s email is used as the sender if available, otherwise a default email is used.  
            - Emails are sent using BCC for privacy.
            """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["subject", "message"],
            properties={
                "subject": openapi.Schema(type=openapi.TYPE_STRING, description="Subject of the newsletter"),
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Message content (HTML supported)"),
            },
        ),
        responses={
            200: openapi.Response(description="Email sent successfully"),
            400: openapi.Response(description="Error sending email"),
        },
    )
    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')

        subscribed_emails = list(SubscribedUsers.objects.values_list('email', flat=True))

        user_email = request.user.email if request.user.is_authenticated and request.user.email else 'default@example.com'
        mail = EmailMessage(subject, message, f"Meru University Science Innovators Club <{user_email}>", bcc=subscribed_emails)
        mail.content_subtype = 'html'

        if mail.send():
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'There was an error sending the email'}, status=status.HTTP_400_BAD_REQUEST)

class SubscribeView(views.APIView):
    @swagger_auto_schema(
        tags=["Newsletters"],
        operation_summary="Subscribe to newsletters",
        operation_description="""
            Allows a user to subscribe to newsletters by providing a valid email.  
            - Validates email format.  
            - Rejects duplicate subscriptions.  
            - Stores email in the database.
            """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL,description="Email to subscribe"),
            },
        ),
        responses={
            201: openapi.Response(description="Email subscribed successfully"),
            400: openapi.Response(description="Invalid or duplicate email"),
        },
    )
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'message': 'Please enter a valid email address to subscribe to our Newsletters!'}, status=status.HTTP_400_BAD_REQUEST)

        if SubscribedUsers.objects.filter(email=email).exists():
            return Response({'message': f'{email} email address is already a subscriber'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError as e:
            return Response({'message': e.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

        subscribe_model_instance = SubscribedUsers(email=email)
        subscribe_model_instance.save()

        return Response({'message': f'{email} email was successfully subscribed to our newsletter!'}, status=status.HTTP_201_CREATED)

class ContactView(views.APIView):
    @swagger_auto_schema(
        tags=["Contact"],
        operation_summary="Send a contact message to the admin",
        operation_description="""
            Sends a contact message from a user to the admin.  
            - Requires `name`, `email`, and `message`.  
            - Forwards the message to predefined admin emails.  
            - Useful for general inquiries, feedback, or support.
            """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email", "message"],
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Sender’s name"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL,description="Sender’s email"),
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Message content"),
            },
        ),
        responses={
            200: openapi.Response(description="Message sent successfully"),
            400: openapi.Response(description="Error sending message"),
        },
    )
    def post(self, request):
        message_name = request.data.get('name')
        message_email = request.data.get('email')
        message = request.data.get('message')

        send_mail(
            message_name,
            message,
            message_email,
            ['ondeyostephen0@gmail.com','innovatorsmust@gmail.com']
        )

        return Response({'message_name': message_name}, status=status.HTTP_200_OK)




