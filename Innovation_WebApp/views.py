from rest_framework import viewsets, views, status
from .serializers import CommunityJoinSerializer, CommunityMemberListSerializer, CommunityMemberSerializer,CommunityProfileSerializer
from .models import CommunityMember, SubscribedUsers,CommunityProfile
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
import logging
logger = logging.getLogger(__name__)
import boto3
from Club.models import ExecutiveMember
from django.shortcuts import get_object_or_404
s3_client = boto3.client('s3')
from account.models import User
from django.db import transaction



    


class NewsletterSendView(views.APIView):
    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')

        # Retrieve all subscribed email addresses
        subscribed_emails = list(SubscribedUsers.objects.values_list('email', flat=True))

        user_email = request.user.email if request.user.is_authenticated and request.user.email else 'default@example.com'
        mail = EmailMessage(subject, message, f"Meru University Science Innovators Club <{user_email}>", bcc=subscribed_emails)
        mail.content_subtype = 'html'

        if mail.send():
            return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'There was an error sending the email'}, status=status.HTTP_400_BAD_REQUEST)

class SubscribeView(views.APIView):
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
    def post(self, request):
        message_name = request.data.get('name')
        message_email = request.data.get('email')
        message = request.data.get('message')

        send_mail(
            message_name,
            message,
            message_email,
            ['ondeyostephen0@gmail.com']
        )

        return Response({'message_name': message_name}, status=status.HTTP_200_OK)


DEFAULT_CLUB_ID = 1
class CommunityProfileViewSet(viewsets.ModelViewSet):
    queryset = CommunityProfile.objects.all().order_by('id')
    serializer_class = CommunityProfileSerializer

    def create(self, request, *args, **kwargs):
        print(f"View - Request data: {request.data}")
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                print(f"View - Initial data: {serializer.initial_data}")
                if serializer.is_valid():
                    print(f"View - Validated data: {serializer.validated_data}")

                    # Validate executive conflicts using IDs
                    community_lead_id = serializer.validated_data.get('community_lead')
                    co_lead_id = serializer.validated_data.get('co_lead')
                    secretary_id = serializer.validated_data.get('secretary')

                    # Check if any of the users are already executives
                    if community_lead_id:
                        community_lead = get_object_or_404(User, id=community_lead_id)
                        if ExecutiveMember.objects.filter(user=community_lead).exists():
                            return Response({
                                'message': f'User {community_lead.email} is already an executive in another community',
                                'status': 'failed',
                                'data': None
                            }, status=status.HTTP_400_BAD_REQUEST)

                    if co_lead_id:
                        co_lead = get_object_or_404(User, id=co_lead_id)
                        if ExecutiveMember.objects.filter(user=co_lead).exists():
                            return Response({
                                'message': f'User {co_lead.email} is already an executive in another community',
                                'status': 'failed',
                                'data': None
                            }, status=status.HTTP_400_BAD_REQUEST)

                    if secretary_id:
                        secretary = get_object_or_404(User, id=secretary_id)
                        if ExecutiveMember.objects.filter(user=secretary).exists():
                            return Response({
                                'message': f'User {secretary.email} is already an executive in another community',
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

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                
                if serializer.is_valid():
                    # Validate executive conflicts using IDs
                    community_lead_id = serializer.validated_data.get('community_lead')
                    co_lead_id = serializer.validated_data.get('co_lead')
                    secretary_id = serializer.validated_data.get('secretary')

                    # Check if any new executives are already executives in other communities
                    if community_lead_id and community_lead_id != instance.community_lead_id:
                        community_lead = get_object_or_404(User, id=community_lead_id)
                        if ExecutiveMember.objects.filter(user=community_lead).exclude(community=instance).exists():
                            return Response({
                                'message': f'User {community_lead.email} is already an executive in another community',
                                'status': 'failed',
                                'data': None
                            }, status=status.HTTP_400_BAD_REQUEST)

                    if co_lead_id and co_lead_id != instance.co_lead_id:
                        co_lead = get_object_or_404(User, id=co_lead_id)
                        if ExecutiveMember.objects.filter(user=co_lead).exclude(community=instance).exists():
                            return Response({
                                'message': f'User {co_lead.email} is already an executive in another community',
                                'status': 'failed',
                                'data': None
                            }, status=status.HTTP_400_BAD_REQUEST)

                    if secretary_id and secretary_id != instance.secretary_id:
                        secretary = get_object_or_404(User, id=secretary_id)
                        if ExecutiveMember.objects.filter(user=secretary).exclude(community=instance).exists():
                            return Response({
                                'message': f'User {secretary.email} is already an executive in another community',
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

        except Exception as e:
            return Response({
                'message': f'Error updating community: {str(e)}',
                'status': 'failed',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self,request,*args,**kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page,many=True)
                paginated_data = self.paginator.get_paginated_response(serializer.data)

                return Response({
                    'message':'Communities retrieved successfully',
                    'status':'success',
                    'data':{
                        'count':paginated_data.data['count'],
                        'next':paginated_data.data['next'],
                        'previous':paginated_data.data['previous'],
                        'results':paginated_data.data['results']
                    }
                },status=status.HTTP_200_OK)
            serializer = self.get_serializer(queryset,many=True)
            return Response({
                'message':'Communities retrieved successfully',
                'status':'success',
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'message':f'Error retrieving communities',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                'message':'Community retrieved successfully',
                'status':'success',
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except CommunityProfile.DoesNotExist:
            return Response({
                'message':'Community not found',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
        
    
    def perfom_update(self,request,*args,**kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data,partial=True)
            if serializer.is_valid():
                self.perfom_update(serializer)
                return Response({
                    "message":"Community updated successfully",
                    "status":"success",
                    "data":serializer.data
                },status=status.HTTP_200_OK)
            
            error_messages = "\n".join(
                f"{field}:{', '.join(errors)}" for field, errors in serializer.errors.item()
            )
            return Response({
                "message":f'community update failed:{error_messages}',
                "status":"failed",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
        except CommunityProfile.DoesNotExist:
            return Response({
                "message":f'Community not found',
                "status":"failed",
                "data":None
            },status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message":f'Error updating community: {str(e)}',
                "status":"failed",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], url_path='search-community')
    def search_by_name(self,request,name=None):
        try:
            name = request.query_params.get('name',None)
            if not name:
                return Response({
                    "message":"Pleasee provide a community name too search",
                    "status":"failed",
                    "data":None
                },status=status.HTTP_400_BAD_REQUEST)
            community = CommunityProfile.objects.get(name__iexact=name)
            serializer = self.get_serializer(community)
            return Response({
                "name":"Community retrieved successfully",
                "status":"success",
                "data":serializer.data
            },status=status.HTTP_200_OK)
        except CommunityProfile.DoesNotExist:
            return Response({
                "message":f'community with name "{name}" not found',
                "status":"failed",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message":f'Error retrieving community:{str(e)}',
                "status":"failed",
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
        
    
class SessionCreateView(APIView):
    def post(self, request, community_id):
        try:
            # Retrieve the community by its ID
            community = CommunityProfile.objects.get(id=community_id)
            
            # Serialize the session data
            session_serializer = CommunityProfileSerializer(data=request.data, context={'request': request})
            if session_serializer.is_valid():
                # Save the session and associate it with the community
                session_serializer.save(community=community)
                #return Response(session_serializer.data, status=status.HTTP_201_CREATED)
                return Response({
                    'message':'Session Updated Successfully',
                    'status':'success',
                    'data':session_serializer.data
                },status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message':session_serializer.errors,
                    'status':'failed',
                    'data':None
                })
            

        except CommunityProfile.DoesNotExist:
            return Response({
                'message':'Commmunity not found',
                'status':'failed',
                'data':None
            },status=status.HTTP_400_BAD_REQUEST)
            
        

    

class CommunityMembersView(APIView):
    def get(self, request, pk):
        try:
            community = CommunityProfile.objects.get(pk=pk)
        except CommunityProfile.DoesNotExist:
            return Response({"error": "Community not found"}, status=status.HTTP_404_NOT_FOUND)

        members = community.members.all()  # Fetch related members
        serializer = CommunityMemberSerializer(members, many=True)
        return Response({
            'message':'Members retrieved successfully',
            'status':'success',
            'data':serializer.data
        },status=status.HTTP_200_OK)
        
    

class JoinCommunityView(APIView):
    def post(self, request, *args, **kwargs):
        community_id = kwargs.get('pk')
        user_email = request.data.get('email')
        
        try:
            community = CommunityProfile.objects.get(id=community_id)
        except CommunityProfile.DoesNotExist:
            return Response(
                {"error": "Community not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # count the number of communities the user has joined
        user_community_count = CommunityMember.objects.filter(email=user_email).count()

        if user_community_count >= 3:
            return Response({
                "message": "You cannot join more than 3 communities."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CommunityJoinSerializer(data={
            'community': community.id,
            'name': request.data.get('name'),
            'email': request.data.get('email')
        })
        
        if serializer.is_valid():
            member = serializer.save(community=community)
            community.update_total_members()
            
            # Get updated community with members list
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


