from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Club,ExecutiveMember
from .serializers import ClubSerializer, ExecutiveMemberSerializer
from rest_framework.decorators import action
# Create your views here.

# Default club ID (Meru University Science Innovators Club)
DEFAULT_CLUB_ID = 1

class ClubDetailView(APIView):

    @swagger_auto_schema(
        tags=["Club"],
        operation_summary="Create a new club",
        operation_description="Creates a new club with the provided details.",
        request_body=ClubSerializer,
        responses={
            201: openapi.Response(
                description="Club created successfully",
                examples={
                    "application/json": {
                        "message": "Club created successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Meru University Science Innovators Club",
                            "about_us": "We are a community of technology enthusiasts dedicated to innovation.",
                            "vision": "To become a leading hub for technological innovation.",
                            "mission": "Empowering members through mentorship and hands-on projects.",
                            "social_media": [
                                {"platform": "LinkedIn", "url": "https://linkedin.com/company/innovators"},
                                {"platform": "Twitter", "url": "https://twitter.com/innovators"}
                            ],
                            "communities": []
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "message": "Club Creation failed: {'name': ['This field is required.']}",
                        "status": "failed",
                        "data": None
                    }
                }
            )
        }
    )
    def post(self,request):
        serializer = ClubSerializer(data=request.data)
        if serializer.is_valid():
            club = serializer.save()
            return Response({
                'messsage':'Club created succssfully',
                'status':'succcess',
                'data':serializer.data
            },status=status.HTTP_201_CREATED)
        return Response({
            'message':f'Club Creation failed:{serializer.errors}',
            'status':'failed',
            'data':None
        },status=status.HTTP_400_BAD_REQUEST)
    """
    View to retrieve, update , or delete club details
    Since we're only dealing with one club, we'll always use the default ID.
    """

    @swagger_auto_schema(
        tags=["Club"],
        operation_summary="Retrieve club details",
        operation_description="Retrieve details of the default club (includes nested communities, members, and sessions).",
        responses={
            200: openapi.Response(
                description="Club retrieved successfully",
                examples={
                    "application/json": {
                        "message": "Club retrieved successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Meru University Science Innovators Club",
                            "about_us": "We are a community of technology enthusiasts dedicated to innovation.",
                            "vision": "To become a leading hub for technological innovation.",
                            "mission": "Empowering members through mentorship and hands-on projects.",
                            "social_media": [
                                {"platform": "LinkedIn", "url": "https://linkedin.com/company/innovators"},
                                {"platform": "Twitter", "url": "https://twitter.com/innovators"}
                            ],
                            "communities": [
                                {
                                    "id": 1,
                                    "name": "Cybersecurity Community",
                                    "community_lead_details": {"id": 2, "name": "Alice Doe",
                                                               "email": "alice@example.com"},
                                    "co_lead_details": {"id": 3, "name": "Bob Smith", "email": "bob@example.com"},
                                    "secretary_details": {"id": 4, "name": "Carol Jones", "email": "carol@example.com"},
                                    "email": "cyber@example.com",
                                    "phone_number": "0712345678",
                                    "description": "A group focused on cybersecurity awareness.",
                                    "founding_date": "2023-05-10",
                                    "is_recruiting": True,
                                    "tech_stack": ["Wireshark", "Nmap", "Burp Suite"],
                                    "members": [{"id": 10, "name": "John Doe"}],
                                    "total_members": 1,
                                    "sessions": [
                                        {
                                            "day": "Monday",
                                            "start_time": "18:00",
                                            "end_time": "19:00",
                                            "meeting_type": "VIRTUAL",
                                            "location": "Google Meet"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            )
        }
    )
    def get(self, request):
        club = get_object_or_404(
            Club.objects.prefetch_related(
                'communities_from_communities_app',
                'communities_from_communities_app__community_lead',
                'communities_from_communities_app__co_lead',
                'communities_from_communities_app__secretary',
                'communities_from_communities_app__social_media',
                'communities_from_communities_app__members',
                'communities_from_communities_app__sessions'
            ), 
        id=DEFAULT_CLUB_ID
    )
        serializer = ClubSerializer(club)
        return Response({
            'message': 'Club retrieved successfully',
            'status': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        tags=["Club"],
        operation_summary="Update club details",
        operation_description="Update the default club's details. Requires full payload.",
        request_body=ClubSerializer,
        responses={
            200: openapi.Response(
                description="Club updated successfully",
                examples={
                    "application/json": {
                        "message": "Club updated successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Updated Club Name",
                            "about_us": "Updated about us text",
                            "vision": "Updated vision",
                            "mission": "Updated mission",
                            "social_media": [
                                {"platform": "LinkedIn", "url": "https://linkedin.com/company/updated"}
                            ],
                            "communities": []
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "message": "Club update failed: {'name': ['This field is required.']}",
                        "status": "failed",
                        "data": None
                    }
                }
            )
        }
    )
    def put(self, request):
        club = get_object_or_404(Club, id=DEFAULT_CLUB_ID)
        serializer = ClubSerializer(club, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Club updated successfully',
                'status': 'success',
                'data': serializer.data
            })
        return Response({
            'message': f'Club update failed: {serializer.errors}',
            'status': 'failed',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Club"],
        operation_summary="Delete the club",
        operation_description="Delete the default club. This action is irreversible.",
        responses={
            204: openapi.Response(
                description="Club deleted successfully",
                examples={
                    "application/json": {"message": "Club deleted successfully", "status": "success", "data": None}}
            ),
            404: openapi.Response(
                description="Club not found",
                examples={"application/json": {"message": "Not found.", "status": "failed", "data": None}}
            )
        }
    )
    def delete(self, request):
        club = get_object_or_404(Club, id=DEFAULT_CLUB_ID)
        club.delete()
        return Response({
            'message': 'Club deleted successfully',
            'status': 'success',
            'data': None
        }, status=status.HTTP_204_NO_CONTENT)


    @swagger_auto_schema(
        tags=["Club"],
        operation_summary="Partially update club details",
        operation_description=(
            "Partially update the default club's details. "
            "Only the provided fields will be updated."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING, example="Updated Club Name"),
                "about_us": openapi.Schema(type=openapi.TYPE_STRING, example="Updated about us text"),
                "vision": openapi.Schema(type=openapi.TYPE_STRING, example="Updated vision"),
                "mission": openapi.Schema(type=openapi.TYPE_STRING, example="Updated mission"),
                "social_media": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "platform": openapi.Schema(type=openapi.TYPE_STRING, example="LinkedIn"),
                            "url": openapi.Schema(type=openapi.TYPE_STRING, example="https://linkedin.com/company/updated")
                        }
                    )
                ),
            },
            required=[]
        ),
        responses={
            200: openapi.Response(
                description="Club partially updated successfully",
                examples={
                    "application/json": {
                        "message": "Club updated successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Updated Club Name",
                            "about_us": "Updated about us text",
                            "vision": "Updated vision",
                            "mission": "Updated mission",
                            "social_media": [
                                {"platform": "LinkedIn", "url": "https://linkedin.com/company/updated"}
                            ],
                            "communities": []
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "message": "Club update failed: {'name': ['This field must be unique.']}",
                        "status": "failed",
                        "data": None
                    }
                }
            )
        }
    )
    def patch(self, request):
        club = get_object_or_404(Club, id=DEFAULT_CLUB_ID)
        serializer = ClubSerializer(club, data=request.data, partial=True)  # 👈 partial=True
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Club updated successfully",
                "status": "success",
                "data": serializer.data
            })
        return Response({
            "message": f"Club update failed: {serializer.errors}",
            "status": "failed",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)


class ExecutiveMemberViewSet(viewsets.ModelViewSet):
    queryset = ExecutiveMember.objects.all()
    serializer_class = ExecutiveMemberSerializer
    """
        A viewset for managing executive members.

        Provides default actions:
        - **list**: Get all executive members.
        - **retrieve**: Get a single executive member by ID.
        - **create**: Create a new executive member.
        - **update/partial_update**: Update an executive member.
        - **destroy**: Delete an executive member.

        Custom actions:
        - **check_email**: Verify if a user (by email) is an executive member.
        """

    queryset = ExecutiveMember.objects.all()
    serializer_class = ExecutiveMemberSerializer

    @swagger_auto_schema(
        operation_summary="Create an executive member",
        operation_description="Create a new executive member record.",
        tags=["Executive Members"],
        request_body=ExecutiveMemberSerializer,
        responses={
            201: openapi.Response(
                description="Executive member created successfully",
                examples={
                    "application/json": {
                        "message": "Executive member created successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "position": "President"
                        }
                    }
                },
            ),
            400: "Validation error"
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response({
                    'message': 'Executive member created successfully',
                    'status': 'success',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

            error_messages = "\n".join(
                f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
            )
            return Response({
                'message': f'Executive member creation failed: {error_messages}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': f'Error creating executive member: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="List executive members",
        operation_description="Retrieve a list of all executive members.",
        tags=["Executive Members"],
        responses={
            200: openapi.Response(
                description="List of executive members",
                examples={
                    "application/json": {
                        "message": "Executive members retrieved successfully",
                        "status": "success",
                        "data": [
                            {"id": 1, "name": "John Doe", "email": "john@example.com", "position": "President"},
                            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "position": "Treasurer"}
                        ]
                    }
                },
            )
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Executive members retrieved successfully',
            'status': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary="Retrieve an executive member",
        operation_description="Retrieve a single executive member by ID.",
        tags=["Executive Members"],
        responses={
            200: openapi.Response(
                description="Executive member retrieved successfully",
                examples={
                    "application/json": {
                        "message": "Executive member retrieved successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "position": "President"
                        }
                    }
                },
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'message': 'Executive member retrieved successfully',
            'status': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary="Update an executive member",
        operation_description="Update an existing executive member record.",
        tags=["Executive Members"],
        request_body=ExecutiveMemberSerializer,
        responses={
            200: openapi.Response(
                description="Executive member updated successfully",
                examples={
                    "application/json": {
                        "message": "Executive member updated successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "position": "President"
                        }
                    }
                },
            ),
            400: "Validation error"
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({
                    'message': 'Executive member updated successfully',
                    'status': 'success',
                    'data': serializer.data
                })

            error_messages = "\n".join(
                f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
            )
            return Response({
                'message': f'Executive member update failed: {error_messages}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': f'Error updating executive member: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete an executive member",
        operation_description="Delete an executive member by ID.",
        tags=["Executive Members"],
        responses={
            204: openapi.Response(
                description="Executive member deleted successfully",
                examples={
                    "application/json": {
                        "message": "Executive member deleted successfully",
                        "status": "success",
                        "data": None
                    }
                },
            ),
            400: "Error deleting member"
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'message': 'Executive member deleted successfully',
                'status': 'success',
                'data': None
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'message': f'Error deleting executive member: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        method="post",
        operation_summary="Check if a user is an executive member",
        operation_description="Check whether a given email belongs to an executive member.",
        tags=["Executive Members"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email address")
            },
            required=["email"]
        ),
        responses={
            200: openapi.Response(
                description="Check result",
                examples={
                    "application/json": {
                        "message": "User is an executive member",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "position": "President"
                        },
                        "is_executive": True
                    }
                },
            ),
            400: "Invalid request"
        }
    )
    @action(detail=False, methods=['post'], url_path='check-email')
    def check_email(self,request):
        try:
            email = request.data.get('email')

            if not email:
                return Response({
                    "message":"Email if required",
                    "status":"failed",
                    "data":None
                },status=status.HTTP_400_BAD_REQUEST)

            executive = ExecutiveMember.objects.filter(email=email).first()

            if executive:
                serializer = self.get_serializer(executive)
                return Response({
                    "message":"User is an executive member",
                    "status":"success",
                    "data":serializer.data,
                    "is_executive":True
                })
            else:
                return Response({
                    "message":"User is not an executive member",
                    "status":"success",
                    "data":None,
                    "is_executive":False
                })
        except Exception as e:
            return Response({
                "message":f'Error checking executive status',
                "status":"failed",
                "data":None,
            }, status=status.HTTP_400_BAD_REQUEST)
