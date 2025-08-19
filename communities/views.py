from rest_framework.views import APIView
from .models import CommunityProfile,CommunityMember
from .serializers import CommunityProfileSerializer,CommunityJoinSerializer,CommunityMemberListSerializer
from django.db import transaction
from Club.models import ExecutiveMember
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.


DEFAULT_CLUB_ID = 1
class CommunityProfileViewSet(viewsets.ModelViewSet):
    queryset = CommunityProfile.objects.all().order_by('id')
    serializer_class = CommunityProfileSerializer

    @swagger_auto_schema(
        tags=["Communities"],
        operation_summary="Create a new Community profile",
        operation_description="""
        Creates a new community profile for the Meru University Science Innovators Club.  
        Restrictions:
        - A user cannot serve as `community_lead`, `co_lead`, or `secretary` if they are already an executive in another community.
        """,
        request_body=CommunityProfileSerializer,
        responses={
            200: openapi.Response(
                description="Community created successfully",
                examples={
                    "application/json":{
                        "message":"community created successfully",
                        "status":"success",
                        "data":{
                            "id": 1,
                            "name": "Cybersecurity Community",
                            "community_lead": 3,
                            "co_lead": 4,
                            "secretary": 5,
                            "email": "cybersec@example.com",
                            "phone_number": "0700123456",
                            "tech_stack": ["Python", "Django", "React"]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error or user already an executive",
                examples={
                    "application/json":{
                        "message":"User john@example.com is already an executive in another community",
                        "status":"failed",
                        "data":None
                    }
                }
            ),
            500: openapi.Response(
                description="server error",
                examples={
                    "application/json":{
                        "message":"Error creating community: Internal server error",
                        "status":"failed",
                        "data":None
                    }
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        print(f"View - Request data: {request.data}")
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                print(f"View - Initial data: {serializer.initial_data}")

                if serializer.is_valid():
                    print(f"View - Validated data: {serializer.validated_data}")
                    community_lead_id = serializer.validated_data.get('community_lead')
                    co_lead_id = serializer.validated_data.get('co_lead')
                    secretary_id = serializer.validated_data.get('secretary')

                    if community_lead_id and ExecutiveMember.objects.filter(user=community_lead_id).exists():
                        return Response({
                            'message': f'User {community_lead_id.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if co_lead_id and ExecutiveMember.objects.filter(user=co_lead_id).exists():
                        return Response({
                            'message': f'User {co_lead_id.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if secretary_id and ExecutiveMember.objects.filter(user=secretary_id).exists():
                        return Response({
                            'message': f'User {secretary_id.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)
                    community = serializer.save()
                    print(f"View - Community created: {community}")

                    return Response({
                        'message': 'Community created successfully',
                        'status': 'success',
                        'data': self.get_serializer(community).data
                    }, status=status.HTTP_201_CREATED)

                error_messages = "\n".join(
                    f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
                )
                print(f"View - Validation errors: {serializer.errors}")
                return Response({
                    'message': f'Community creation failed: {error_messages}',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"View - Exception: {str(e)}")
            return Response({
                'message': f'Error creating community: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update a community",
        operation_description="""
            Update the details of a community (partial update allowed).  

            - Ensures that `community_lead`, `co_lead`, and `secretary` are unique 
              across different communities.  
            - Prevents assigning a user as an executive in more than one community.  
            - Uses database transactions to maintain data integrity.  

            **Validation rules:**  
            - A user cannot be assigned as `community_lead`, `co_lead`, or `secretary` 
              in more than one community.  
            - Partial updates are supported.  

            **Responses:**  
            - 200: Community updated successfully  
            - 400: Validation or assignment error  
            - 404: Community not found  
            - 500: Internal server error  
            """,
        request_body=CommunityProfileSerializer,
        responses={
            200: openapi.Response("Community updated successfully"),
            400: openapi.Response("Validation or assignment error"),
            404: openapi.Response("Community not found"),
            500: openapi.Response("Internal server error"),
        },
        tags=["Communities"]
    )
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=True)

                if serializer.is_valid():
                    new_community_lead = serializer.validated_data.get('community_lead')
                    new_co_lead = serializer.validated_data.get('co_lead')
                    new_secretary = serializer.validated_data.get('secretary')
                    if (
                            new_community_lead
                            and new_community_lead != instance.community_lead
                            and ExecutiveMember.objects.filter(user=new_community_lead).exclude(
                        community=instance).exists()
                    ):
                        return Response({
                            'message': f'User {new_community_lead.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if (
                            new_co_lead
                            and new_co_lead != instance.co_lead
                            and ExecutiveMember.objects.filter(user=new_co_lead).exclude(community=instance).exists()
                    ):
                        return Response({
                            'message': f'User {new_co_lead.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if (
                            new_secretary
                            and new_secretary != instance.secretary
                            and ExecutiveMember.objects.filter(user=new_secretary).exclude(community=instance).exists()
                    ):
                        return Response({
                            'message': f'User {new_secretary.email} is already an executive in another community',
                            'status': 'failed',
                            'data': None
                        }, status=status.HTTP_400_BAD_REQUEST)

                    updated_community = serializer.save()

                    return Response({
                        'message': 'Community updated successfully',
                        'status': 'success',
                        'data': self.get_serializer(updated_community).data
                    }, status=status.HTTP_200_OK)

                error_messages = "\n".join(
                    f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()
                )
                return Response({
                    'message': f'Community update failed: {error_messages}',
                    'status': 'failed',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        except CommunityProfile.DoesNotExist:
            return Response({
                'message': 'Community not found',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'message': f'Error updating community: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=["Communities"],
        operation_summary="Retrieve all community profiles",
        operation_description="""
        Returns a list of all community profiles.  
        - Supports pagination (`limit` & `offset` if pagination is enabled).  
        - Response includes metadata such as `count`, `next`, and `previous` when paginated.  
        """,
        manual_parameters=[
            openapi.Parameter(
                "page",openapi.IN_QUERY,description="Page number for paginated results",type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size", openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of communities retrieved successfully",
                examples={
                    "application/json":{
                        "message":"Communities retrieved successfully",
                        "status":"success",
                        "data":{
                            "count":2,
                            "next":"http://localhost:8000/api/communities/?page=2",
                            "previous":None,
                            "results":[
                                {
                                    "id": 1,
                                    "name": "Cybersecurity Community",
                                    "community_lead": 3,
                                    "co_lead": 4,
                                    "secretary": 5,
                                    "email": "cybersec@example.com",
                                    "phone_number": "0700123456",
                                    "tech_stack": ["Python", "Django"]
                                },
                                {
                                    "id": 2,
                                    "name": "AI & Data Science Community",
                                    "community_lead": 6,
                                    "co_lead": 7,
                                    "secretary": 8,
                                    "email": "aids@example.com",
                                    "phone_number": "0712345678",
                                    "tech_stack": ["TensorFlow", "Pandas"]
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Error retrieving communities",
                examples={
                    "application/json":{
                        "message":"Error retrieving communities",
                        "status":"failed",
                        "data":None
                    }
                }
            )
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
                    'message': 'Communities retrieved successfully',
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
                'message': 'Communities retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message': f'Error retrieving communities',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Communities"],
        operation_summary="Retrieve a single community profile",
        operation_description="""
        Retrieves details of a specific community profile by its **ID**.  
        If the given ID does not exist, a `Community not found` error will be returned. 
        """,
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Unique ID of the community profile",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Community retrieved successfully",
                examples={
                    "application/json": {
                        "message": "Community retrieved successfully",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Cybersecurity Community",
                            "community_lead": 3,
                            "co_lead": 4,
                            "secretary": 5,
                            "email": "cybersec@example.com",
                            "phone_number": "0700123456",
                            "tech_stack": ["Python", "Django"]
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Community not found",
                examples={
                    "application/json": {
                        "message": "Community not found",
                        "status": "failed",
                        "data": None
                    }
                }
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                'message': 'Community retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except CommunityProfile.DoesNotExist:
            return Response({
                'message': 'Community not found',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="get",
        operation_summary="Search community by name",
        operation_description="""
        Searches for a community profile by its **exact name** (case-insensitive).  

        Query Parameter:  
        - `name`: Community name to search (required).  
        """,
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                description="Community name to search (case-insensitive)",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Community retrieved successfully",
                examples={
                    "application/json": {
                        "message": "Community retrieved successfully",
                        "status": "success",
                        "data": {
                            "id": 2,
                            "name": "Cybersecurity Community",
                            "community_lead": 3,
                            "co_lead": 4,
                            "secretary": 5,
                            "email": "cybersec@example.com",
                            "phone_number": "0700123456",
                            "tech_stack": ["Python", "Django"]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Missing or invalid query parameter / Not found",
                examples={
                    "application/json": {
                        "message": 'community with name "AI Club" not found',
                        "status": "failed",
                        "data": None
                    }
                }
            )
        },
        tags=["Communities"]
    )
    @action(detail=False, methods=['get'], url_path='search-community')
    def search_by_name(self, request, name=None):
        try:
            name = request.query_params.get('name', None)
            if not name:
                return Response({
                    "message": "Please provide a community name to search",
                    "status": "failed",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
            community = CommunityProfile.objects.get(name__iexact=name)
            serializer = self.get_serializer(community)
            return Response({
                "message": "Community retrieved successfully",
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except CommunityProfile.DoesNotExist:
            return Response({
                "message": f'community with name "{name}" not found',
                "status": "failed",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": f'Error retrieving community: {str(e)}',
                "status": "failed",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)


class JoinCommunityView(APIView):

    @swagger_auto_schema(
        tags=["Communities"],
        operation_summary="Join a community",
        operation_description="""
               Allows a user to join a specific community using the community ID and their email address.  

               ### Rules:
               - A user cannot join more than **3 communities**.  
               - If the community does not exist, a **404 Not Found** response is returned.  
               - On successful join, the community's total members count is updated.  

               ### Request Body:
               - **name**: Full name of the user joining the community.  
               - **email**: User's email address.  

               ### Responses:
               - **201 Created**: User successfully joined the community.  
               - **400 Bad Request**: Validation failed, user already in 3 communities, or invalid data.  
               - **404 Not Found**: Community not found.  
               """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email"],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="User's full name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
            },
        ),
        responses={
            201: openapi.Response(
                description="User successfully joined the community",
                examples={
                    "application/json": {
                        "message": "Successfully joined the community!",
                        "status": "success",
                        "data": {
                            "id": 1,
                            "name": "Cybersecurity Community",
                            "email": "Cybersecuriy.community@example.com",
                            "total_members": 25,
                            "tech_stack": ["Kali Linux", "Wireshark"]
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="Invalid data or community limit reached",
                examples={
                    "application/json": {
                        "message": "You cannot join more than 3 communities.",
                        "status": "failed",
                        "data": None
                    }
                },
            ),
            404: openapi.Response(
                description="Community not found",
                examples={
                    "application/json": {
                        "error": "Community not found"
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        community_id = kwargs.get('pk')
        user_email = request.data.get('email')

        try:
            community = CommunityProfile.objects.get(id=community_id)
        except CommunityProfile.DoesNotExist:
            return Response({
                "message": "Community not found",
                "status": "failed",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        user_community_count = CommunityMember.objects.filter(email=user_email).count()

        if user_community_count >= 3:
            return Response({
                "message": "You cannot join more than 3 communities.",
                "status": "failed",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommunityJoinSerializer(data={
            'community': community.id,
            'name': request.data.get('name'),
            'email': request.data.get('email')
        })

        if serializer.is_valid():
            member = serializer.save(community=community)
            community.update_total_members()
            community_serializer = CommunityProfileSerializer(community)

            return Response({
                "message": "Successfully joined the community!",
                'status': 'success',
                'data': community_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': f'There was an error please try again: {serializer.errors}',
            'status': 'failed',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


class CommunityMembersView(APIView):

    @swagger_auto_schema(
        operation_summary="List community members",
        operation_description="""
            Retrieve all members belonging to a specific community.

            ### Path Parameter:
            - `pk` (integer): The unique ID of the community.

            ### Success Response (200):
            Returns a list of members in the given community, along with the total count.

            Example response:
            {
                "status": "success",
                "total_members": 2,
                "data": [
                    {
                        "id": 1,
                        "name": "John Doe",
                        "email": "johndoe@example.com"
                    },
                    {
                        "id": 2,
                        "name": "Jane Smith",
                        "email": "janesmith@example.com"
                    }
                ]
            }

            ### Error Response (404):
            Returned if the given community does not exist.

            Example response:
            {
                "status": "failed",
                "message": "Community not found"
            }
            """,
        tags=["Communities"],
        responses={
            200: openapi.Response(
                description="List of community members",
                examples={
                    "application/json": {
                        "status": "success",
                        "total_members": 2,
                        "data": [
                            {"id": 1, "name": "John Doe", "email": "johndoe@example.com"},
                            {"id": 2, "name": "Jane Smith", "email": "janesmith@example.com"}
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="Community not found",
                examples={
                    "application/json": {
                        "status": "failed",
                        "message": "Community not found"
                    }
                }
            ),
        }
    )
    def get(self, request, pk=None):
        try:
            community = CommunityProfile.objects.get(id=pk)
            members = community.members.all()
            serializer = CommunityMemberListSerializer(members, many=True)

            return Response({
                'status': 'success',
                'total_members': members.count(),
                'data': serializer.data
            })

        except CommunityProfile.DoesNotExist:
            return Response({
                'status': 'failed',
                'message': 'Community not found'
            }, status=status.HTTP_404_NOT_FOUND)
