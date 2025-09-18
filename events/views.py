import csv
import hashlib
import json

import boto3
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Events,EventRegistration
from .serializers import EventsSerializer,EventRegistrationSerializer,MyRegistrationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.http import Http404, HttpResponse, JsonResponse
from django.conf import settings
s3_client = boto3.client('s3')
from rest_framework import viewsets,status
import traceback
from drf_yasg import openapi
# Create your views here.

def generate_events_cache_key(request):
    query_params = request.GET.dict()
    cache_key_data = {
        'endpoint': 'events_list',
        'params': query_params,
        'page': query_params.get('page',1),
        'page_size': query_params.get('page_size','10')
    }
    key_string = json.dumps(cache_key_data,sort_keys=True)
    return f"events_list_{hashlib.md5(key_string.encode()).hexdigest()}"

def generate_event_detail_cache_key(event_id):
    return f"event_detail_{event_id}"

def generate_user_registration_cache_key(user_identifier,identifier_type='email'):
    return f"user_registrations_{identifier_type}_{hashlib.md5(str(user_identifier).encode()).hexdigest()}"


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'message':'Events retrieved successfuly',
            'status':'success',
            'data':{
                'count':self.page.paginator.count,
                'next':self.get_next_link(),
                'previous':self.get_previous_link(),
                'results':data
            }
        })

def generate_s3_image_url(bucket_name, object_key):
    return f"https://{bucket_name}.s3.ap-southeast-2.amazonaws.com/{object_key}"


@method_decorator(csrf_exempt, name='dispatch')
class EventViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    pagination_class = EventPagination
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=["Events"],
        method='post',
        operation_summary="Create a new event",
        operation_description="Upload an event with details and an image. Image is uploaded to S3 and URL is stored.",
        manual_parameters=[
            openapi.Parameter(
                name="image",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Event image file"
            ),
            openapi.Parameter(name="name", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Event name"),
            openapi.Parameter(name="category", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Event category"),
            openapi.Parameter(name="title", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Event title"),
            openapi.Parameter(name="description", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Event description"),
            openapi.Parameter(name="date", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, format="date-time",required=True, description="Event date (ISO format)"),
            openapi.Parameter(name="location", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Event location"),
            openapi.Parameter(name="organizer", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, required=True,description="Organizer name"),
            openapi.Parameter(name="contact_email", in_=openapi.IN_FORM, type=openapi.TYPE_STRING, format="email",required=True, description="Organizer email"),
            openapi.Parameter(name="is_virtual", in_=openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=True,description="Whether the event is virtual"),
        ],
        responses={
            200: openapi.Response("Event created successfully", EventsSerializer),
            400: "Bad Request (e.g missing fields, no image)",
            500: "Server error (e.g upload failed)"
        }
    )
    @action(methods=['post'], detail=False, url_path='add', url_name='add-event')
    def create_event(self, request, *args, **kwargs):
        print("Files in request:", request.FILES)
        print("Data in request:", request.data)
        print("Content-Type:", request.content_type)
        file = request.FILES.get('image')
        if not file:
            return JsonResponse({
                "message": "No image provided",
                "status": "error"
            }, status=400)

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        object_key = f"event_images/{file.name}"
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=file.read(),
                ContentType=file.content_type
            )
        except Exception as e:
            return JsonResponse({
                "message": f"Failed to upload image to S3: {str(e)}",
                "status": "error"
            }, status=500)


        event_data = request.data
        event = Events.objects.create(
            name=event_data['name'],
            category=event_data['category'],
            title=event_data['title'],
            description=event_data['description'],
            date=event_data['date'],
            location=event_data['location'],
            organizer=event_data['organizer'],
            contact_email=event_data['contact_email'],
            is_virtual=event_data['is_virtual'],
            image_url=f"event_images/{file.name}"  # Store the image path in the event
        )

        image_url = generate_s3_image_url(bucket_name, object_key)

        response_data = {
            'message': 'Event Created successfully',
            'status': 'success',
            "data": {
                "id": event.id,
                "image_url": image_url,
                "name": event.name,
                "category": event.category,
                "title": event.title,
                "description": event.description,
                "date": event.date,
                "location": event.location,
                "organizer": event.organizer,
                "contact_email": event.contact_email,
                "is_virtual": event.is_virtual,
            }
        }

        return JsonResponse(response_data)

    @swagger_auto_schema(
        tags=["Events"],
        methods=["put","patch"],
        operation_summary="Update an event",
        operation_description="Update an existing event. You can also upload a new event image which will be stored in AWS S3.",
        request_body=EventsSerializer,
        responses={
            200: openapi.Response(
                description="Event updated successfully",
                schema=EventsSerializer
            ),
            400: "Invalid input / validation error",
            500: "Failed to upload image to S3"
        }
    )
    @action(methods=['put', 'patch'], detail=True, url_path='update', url_name='update-event')
    def update_event(self, request, *args, **kwargs):
        partial = kwargs.get('partial', request.method == 'PATCH')
        instance = self.get_object()
        file = request.FILES.get('image')
        if file:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            object_key = f"event_images/{file.name}"

            try:
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=file.read(),
                    ContentType=file.content_type
                )
                mutable_data = request.data.copy()
                mutable_data['image_url'] = f"event_images/{file.name}"


                serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
            except Exception as e:
                return Response({
                    "message": f"Failed to upload image to S3: {str(e)}",
                    "status": "error",
                    "data": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            event_instance = serializer.save()
            if file:
                image_url = generate_s3_image_url(bucket_name, object_key)
                response_data = EventsSerializer(event_instance).data
                response_data['image_url'] = image_url
            else:
                response_data = EventsSerializer(event_instance).data

            return Response({
                'message': 'Event Updated Successfully',
                'status': 'success',
                'data': response_data
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Event update failed',
            'status': 'error',
            'errors': serializer.errors,
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Events"],
        method='get',
        operation_summary="Retrieves a list of events",
        operation_description="Retrieve a list of all events with pagination support. Each event includes image_url (if uploaded).",
        responses={
            200: openapi.Response(
                description="List of events retrieved successfully",
                schema=EventsSerializer(many=True)
            ),
        }
    )
    @action(detail=False, methods=['get'], url_path='list', url_name='list-events')
    def list_events(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        for event in queryset:
            print(f"Event {event.id} has image_url in DB: {event.image_url}")

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for item in serializer.data:
                print(f"Serialized event {item['id']} has image_url: {item.get('image_url')}")

            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'message': 'Events retrieved successfully',
            'status': 'success',
            'data': {
                'count': queryset.count(),
                'next': None,
                'previous': None,
                'results': serializer.data
            }
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Events"],
        method='delete',
        operation_summary="Deletes an event",
        operation_description="Delete an event by its ID",
        responses={
            204: openapi.Response(
                description="Event deleted successfully",
                examples={
                    "application/json":{
                        "message": "Event deleted successfully",
                        "status":"success",
                        "data": None
                    }
                }
            ),
            400: openapi.Response(
                description="Error deleting event",
                examples={
                    "application/json":{
                        "message":"Error deleting the event",
                        "status":"failed",
                        "data":None
                    }
                }
            ),
        },
    )
    @action(detail=True, methods=['delete'], url_path='delete', url_name='delete-event')
    def destroy_event(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({
                'message': 'Event deleted successfully',
                'status': 'success',
                'data': None
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'message': 'Error deleting the event',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Events"],
        operation_summary="Retrieves an event with its details",
        operation_description="Retrieve details of an event by its ID",
        responses={
            200: openapi.Response(
                description="Event details fetched succcessfully",
                schema=EventsSerializer(),
                examples={
                    "application/json":{
                        "message":"Event details fetched successfully",
                        "status":"success",
                        "data":{
                            "id": 1,
                            "title": "Sample Event",
                            "description": "This is a test event",
                            "date": "2025-08-17T12:00:00Z"
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Error not found",
                examples={
                    "application/json":{
                        "message":"Event not found",
                        "status":"failed",
                        "data":None
                    }
                }
            ),
            400: openapi.Response(
                description="Error fetching event",
                examples={
                    "application/json":{
                        "message":"Error fetching event",
                        "status":"failed",
                        "data":None
                    }
                }
            ),
        },
    )
    @action(detail=True, methods=['get'], url_path='view', url_name='view-event')
    def retrieve_event(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                'message': 'Event details fetched successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Http404:
            return Response({
                'message': 'Event not found',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': f'Error fetching thr event:{str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Name of the event (exact or partial match)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response("Event details fetched successfully", EventsSerializer),
            400: "Bad Request (Missing or invalid parameters)",
            404: "Event not found"
        },
        operation_summary="Get event by name",
        operation_description="Retrieve an event by its name (case-insensitive search, supports partial match)."
    )
    @action(detail=False, methods=['get'], url_path='by-name', url_name='event-by-name')
    def get_event_by_name(self, request):
        try:
            event_name = request.query_params.get('name')
            print(f"Searching for event with name: {event_name}")  # Debug print

            if not event_name:
                return Response({
                    'message': 'Name parameter is required',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            instance = Events.objects.filter(
                Q(name__iexact=event_name) |
                Q(name__icontains=event_name)
            ).first()

            if not instance:
                return Response({
                    'message': f'Event with name "{event_name}" not found',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(instance)

            return Response({
                'message': 'Event details fetched successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in get_event_by_name: {str(e)}")  # Debug print
            return Response({
                'message': f'Error fetching the event: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer

    @swagger_auto_schema(
        tags=["Event Registration"],
        operation_summary="Registers a user for a specific event",
        operation_description="Registers a user for a specific event",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "full_name", "phone_number", "course", "educational_level"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL,description="Attendee email"),
                "full_name": openapi.Schema(type=openapi.TYPE_STRING, description="Full name of the attendee"),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="Phone number"),
                "course": openapi.Schema(type=openapi.TYPE_STRING, description="Course of study"),
                "educational_level": openapi.Schema(type=openapi.TYPE_STRING, description="Educational level"),
                "expectations": openapi.Schema(type=openapi.TYPE_STRING, description="Expectations from the event"),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successfully registered an event",
                examples = {
                    "application/json":{
                        "message": "successfully registered for the event",
                        "status": "success",
                        "data": {
                            "eventName": "Tech Innovation Summit",
                            "eventDescription": "A summit on innovation",
                            "eventLocation": "Meru University Hall",
                            "eventDate": "2025-09-01T10:00:00Z",
                            "course": "Computer Science",
                            "educational_level": "Undergraduate",
                            "email": "john@example.com",
                            "event": 1,
                            "expectations": "Networking and learning",
                            "full_name": "John Doe",
                            "phone_number": "+254700000000",
                            "registration_timestamp": "2025-08-17T12:00:00Z",
                            "ticket_number": "12345",
                            "uid": "abc123-uuid"
                        }
                    }
                }
            ),
            400: "Bad Request - missing or invalid fields",
            500: "Internal server error"
        }
    )
    def create(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        if not event_pk:
            return Response({
                "message": "Event ID missing in the request URL",
                "status": "failed",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email')
        if not email:
            return Response({
                "message": "Email is required for registration",
                "status": "failed",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        mutable_data = request.data.copy()
        mutable_data['event'] = event_pk

        serializer = self.get_serializer(data=mutable_data)

        if serializer.is_valid():
            try:
                if request.user.is_authenticated:
                    registration = serializer.save(user=request.user)
                else:
                    registration = serializer.save()

                event = registration.event

                return Response({
                    "message": "successfully registered for the event",
                    "status": "success",
                    "data": {
                        "eventName": event.name,
                        "eventDescription": event.description,
                        "eventLocation": event.location,
                        "eventDate": event.date.isoformat(),
                        "course": registration.course,
                        "educational_level": registration.educational_level,
                        "email": registration.email,
                        "event": event.id,
                        "expectations": registration.expectations,
                        "full_name": registration.full_name,
                        "phone_number": registration.phone_number,
                        "registration_timestamp": registration.registration_timestamp.isoformat(),
                        "ticket_number": str(registration.ticket_number),
                        "uid": str(registration.uid)
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                traceback.print_exc()
                print(f'Error during registration process:{str(e)}')
                return Response({
                    "message": f'An error occured registration:{str(e)}',
                    "status": "failed",
                    "data": None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        error_messages = "\n".join(
            f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
        )
        return Response({
            'message': f'Event registration failed: {error_messages}',
            'status': 'failed',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        tags=["Event Registration"],
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'email',
                openapi.IN_QUERY,
                description="Email of the user to fetch registered events",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Registered events retrieved successfully",
                examples={
                    "application/json":{
                        "message":"Registered events retrieved successfully",
                        "status":"success",
                        "data":[
                            {
                                "id": 1,
                                "event": 3,
                                "email": "user@example.com",
                                "registered_at": "2025-08-17T12:30:00Z"
                            }
                        ]
                    }
                }
            ),
            400: "Email parameter is required",
            500: "Internal server error"
        },
        operation_description="Retrieve all events registered by a user using their email.",
        operation_summary="Retrieve all events registered by a user using their email."
    )
    @action(detail=False, methods=['get'], url_path='user-registrations')
    def get_user_registered_events(self, request):
        try:
            email = request.query_params.get('email')
            if not email:
                return Response({
                    'message': 'Email parameter is required',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            registrations = EventRegistration.objects.filter(email=email)

            if not registrations.exists():
                return Response({
                    'message': 'No registered events found for this email',
                    'status': 'success',
                    'data': []
                }, status=status.HTTP_200_OK)
            serializer = EventRegistrationSerializer(registrations, many=True)
            return Response({
                'message': 'Registered events retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': f'Error retrieving events: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=["Event Registration"],
        operation_description="Retrieve all events registered by a user using their User ID.",
        operation_summary="Retrieve all events registered by a user using their User ID.",
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                description="ID of the user to fetch event registration",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="User's registration retrieved successfully",
                examples={
                    "application/json":{
                        "message":"User registrations retrieved successfully",
                        "status":"success",
                        "data":[
                            {
                                "id": 2,
                                "event": 5,
                                "email": "user@example.com",
                                "registered_at": "2025-08-17T12:30:00Z"
                            }
                        ]
                    }
                }
            ),
            404: "User not found",
            400: "User ID is required",
            500: "Internal server error"
        }
    )
    @action(detail=False, methods=['get'], url_path=r'user-events/(?P<user_id>\d+)')
    def get_events_by_user_id(self, request, user_id=None, *args, **kwargs):
        try:
            if not user_id:
                return Response({
                    'message': 'User ID is required',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                user_email = user.email
            except User.DoesNotExist:
                return Response({
                    'message': 'User not found',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            registrations = EventRegistration.objects.filter(email=user_email)

            if not registrations.exists():
                return Response({
                    'message': 'No registrations found for this user',
                    'status': 'success',
                    'data': []
                }, status=status.HTTP_200_OK)
            serializer = self.get_serializer(registrations, many=True)

            return Response({
                'message': 'User registrations retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': f'Error retrieving registrations: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=["Event Registration"],
        operation_description="Retrieve all event registrations for the currently authenticated user.",
        operation_summary="Retrieve all event registrations for the currently authenticated user.",
        method='get',
        responses={
            200: openapi.Response(
                description="Authenticated user's event registrations retrieved successfully",
                examples={
                    "application/json":{
                        "message":"Your registered events retrieved successfully",
                        "status":"success",
                        "data":[
                            {
                                "id":7,
                                "event":{
                                    "id":3,
                                    "title":"Tech Summit",
                                    "date":"2025-09-01"
                                },
                                "registered_at": "2025-08-17T12:30:00Z"
                            }
                        ]
                    }
                }
            ),
            401: "Authentication required",
            500: "Internal server error"
        }
    )
    @action(detail=False, methods=['get'], url_path='my-registrations')
    def get_my_registrations(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'message': 'Authentication required',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_401_UNAUTHORIZED)
            registrations = EventRegistration.objects.filter(user=request.user).select_related('event')

            if not registrations.exists():
                return Response({
                    'message': 'You have no registered events',
                    'status': 'success',
                    'data': []
                }, status=status.HTTP_200_OK)
            serializer = MyRegistrationSerializer(registrations, many=True)

            return Response({
                'message': 'Your registered events retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': f'Error retrieving your registrations: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            return EventRegistration.objects.filter(event_id=event_pk)
        return super().get_queryset()

    @swagger_auto_schema(
        tags=["Event Registration"],
        operation_description="List all event registrations. Supports filtering by event ID if `event_pk` is provided in the URL. Results are paginated.",
        operation_summary="Retrieve all event registrations (with optional event filter)",
    responses={
            200: openapi.Response(
                description="Paginated list of event registrations",
                examples={
                    "application/json": {
                        "message": "Event registrations retrieved successfully",
                        "status": "success",
                        "data": {
                            "count": 25,
                            "next": "http://api.example.com/events/registrations/?page=2",
                            "previous": None,
                            "results": [
                                {
                                    "id": 10,
                                    "event": 3,
                                    "email": "user@example.com",
                                    "registered_at": "2025-08-17T12:30:00Z"
                                }
                            ]
                        }
                    }
                }
            ),
            400: "Error retrieving registrations"
        }
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_data = self.paginator.get_paginated_response(serializer.data)

                return Response({
                    'message': 'Event registrations retrieved successfully',
                    'status': 'success',
                    'data': {
                        'count': paginated_data.data['count'],
                        'next': paginated_data.data['next'],
                        'previous': paginated_data.data['previous'],
                        'results': paginated_data.data['results']
                    }
                }, status=status.HTTP_200_OK)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'message': 'Event registrations retrieved successfully',
                'status': 'success',
                'data': {
                    'count': len(serializer.data),
                    'next': None,
                    'previous': None,
                    'data': serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': f'Error retreiving registrations:{str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Event Registration"],
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'event_pk',
                openapi.IN_PATH,
                description="ID of the event whose registrations should be exported",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="CSV file containing event registrations",
                examples={
                    "text/csv": (
                            "UID,Full Name,Email,Course,Educational Level,Phone Number,Expectations,Registration Date,Ticket Number\n"
                            "12345,John Doe,john@example.com,Computer Science,Undergraduate,0712345678,"
                            "Learn more about AI,2025-08-17T12:30:00Z,TK001\n"
                    )
                }
            ),
            400: "Event ID is required"
        },
        operation_description=(
                "Export all registrations for a given event as a downloadable CSV file.\n\n"
                "Requires the `event_pk` parameter.\n"
                "CSV columns include: UID, Full Name, Email, Course, Educational Level, "
                "Phone Number, Expectations, Registration Date, and Ticket Number."
        ),
        operation_summary="Export event registrations as a CSV file"
    )
    @action(detail=False, methods=['get'], url_path='export')
    def export_registrations(self, request, event_pk=None):
        if not event_pk:
            return Response({"error": "Event ID is required"}, status=400)

        registrations = EventRegistration.objects.filter(event_id=event_pk)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="event_{event_pk}_registrations.csv"'

        writer = csv.writer(response)
        writer.writerow((
            'UID',
            'Full Name',
            'Email',
            'Course',
            'Educational Level',
            'Phone Number',
            'Expectations',
            'Registration Date',
            'Ticket Number'
        ))

        for registration in registrations:
            writer.writerow((
                registration.uid,
                registration.full_name,
                registration.email,
                registration.course,
                registration.educational_level,
                registration.phone_number,
                registration.expectations,
                registration.registration_timestamp,
                registration.ticket_number
            ))

        return response