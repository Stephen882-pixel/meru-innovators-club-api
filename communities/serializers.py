from rest_framework import serializers
from .models import (
    CommunitySession,
    CommunityMember,
    Social_media,
    CommunityProfile
)
from Club.models import ExecutiveMember,Club
from account.models import User



class CommunitySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunitySession
        fields = ['day', 'start_time', 'end_time', 'meeting_type', 'location']
        extra_kwargs = {'community':{'required':False}}

class CommunityMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMember
        fields = ['id', 'name', 'email', 'joined_at']

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social_media
        fields = ['id','platform','url']


class CommunityMemberListSerializer(serializers.ModelSerializer):
    joined_date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = CommunityMember
        fields = ['id', 'name', 'email', 'joined_date']
        read_only_fields = ['id', 'joined_date']


DEFAULT_CLUB_ID = 1
class CommunityProfileSerializer(serializers.ModelSerializer):
    community_lead = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    co_lead = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    secretary = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    community_lead_details = serializers.SerializerMethodField()
    co_lead_details = serializers.SerializerMethodField()
    secretary_details = serializers.SerializerMethodField()

    club = serializers.PrimaryKeyRelatedField(
        queryset=Club.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    social_media = SocialMediaSerializer(many=True, required=False)
    sessions = CommunitySessionSerializer(many=True, required=False)
    members = CommunityMemberListSerializer(many=True, read_only=True)

    class Meta:
        model = CommunityProfile
        fields = [
            'id', 'name', 'club', 'community_lead', 'co_lead', 'secretary',
            'community_lead_details', 'co_lead_details', 'secretary_details',
            'email', 'phone_number', 'social_media', 'description',
            'founding_date', 'total_members', 'members', 'is_recruiting', 'tech_stack',
            'sessions'
        ]
        read_only_fields = ['id', 'total_members', 'community_lead_details',
                            'co_lead_details', 'secretary_details', 'members']


    def get_community_lead_details(self, obj):
        if obj.community_lead:
            return {
                'id': obj.community_lead.id,
                'username': obj.community_lead.username,
                'email': obj.community_lead.email,
                'first_name': obj.community_lead.first_name,
                'last_name': obj.community_lead.last_name
            }
        return None

    def get_co_lead_details(self, obj):
        if obj.co_lead:
            return {
                'id': obj.co_lead.id,
                'username': obj.co_lead.username,
                'email': obj.co_lead.email,
                'first_name': obj.co_lead.first_name,
                'last_name': obj.co_lead.last_name
            }
        return None

    def get_secretary_details(self, obj):
        if obj.secretary:
            return {
                'id': obj.secretary.id,
                'username': obj.secretary.username,
                'email': obj.secretary.email,
                'first_name': obj.secretary.first_name,
                'last_name': obj.secretary.last_name
            }
        return None

    def validate(self, data):
        community_lead_id = data.get('community_lead')
        co_lead_id = data.get('co_lead')
        secretary_id = data.get('secretary')

        if not any([community_lead_id, co_lead_id, secretary_id]):
            raise serializers.ValidationError(
                "At least one executive position (community_lead, co_lead, or secretary) must be assigned."
            )

        executives = [id for id in [community_lead_id, co_lead_id, secretary_id] if id is not None]
        if len(executives) != len(set(executives)):
            raise serializers.ValidationError(
                "A user cannot hold multiple executive positions in the same community."
            )

        return data

    def validate_name(self, value):
        club = self.initial_data.get('club', DEFAULT_CLUB_ID)
        if self.instance is None:
            if CommunityProfile.objects.filter(name=value, club_id=club).exists():
                raise serializers.ValidationError("A community with this name already exists in this club.")
        return value

    def validate_email(self, value):
        if value and CommunityProfile.objects.filter(email=value).exclude(
                id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("This email is already used by another community.")
        return value

    def validate_phone_number(self, value):
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits, +, -, or spaces.")
        return value

    def create(self, validated_data):
        social_media_data = validated_data.pop('social_media', [])
        sessions_data = validated_data.pop('sessions', [])

        community_lead = validated_data.pop('community_lead', None)
        co_lead = validated_data.pop('co_lead', None)
        secretary = validated_data.pop('secretary', None)

        if 'club' not in validated_data or validated_data['club'] is None:
            validated_data['club'] = Club.objects.get(id=DEFAULT_CLUB_ID)

        community = CommunityProfile.objects.create(
            community_lead=community_lead,
            co_lead=co_lead,
            secretary=secretary,
            **validated_data
        )
        community.refresh_from_db()

        try:
            print(f"Community ID after creation: {community.id}")
            print(f"Community club: {community.club}")

            if community_lead:
                print(f"Creating LEAD executive for user: {community_lead}")
                ExecutiveMember.objects.create(
                    user=community_lead,
                    community=community,
                    position='LEAD'
                )
            if co_lead:
                print(f"Creating CO_LEAD executive for user: {co_lead}")
                ExecutiveMember.objects.create(
                    user=co_lead,
                    community=community,
                    position='CO_LEAD'
                )
            if secretary:
                print(f"Creating SECRETARY executive for user: {secretary}")
                ExecutiveMember.objects.create(
                    user=secretary,
                    community=community,
                    position='SECRETARY'
                )
        except Exception as e:
            community.delete()
            raise serializers.ValidationError(f"Error creating executives: {str(e)}")

        try:
            social_media_instances = []
            for sm_data in social_media_data:
                sm_instance, created = Social_media.objects.get_or_create(
                    platform=sm_data['platform'],
                    url=sm_data['url']
                )
                social_media_instances.append(sm_instance)
            community.social_media.set(social_media_instances)
        except Exception as e:
            community.delete()
            raise serializers.ValidationError(f"Error creating social media: {str(e)}")
        try:
            for session_data in sessions_data:
                CommunitySession.objects.create(
                    community=community,
                    day=session_data['day'],
                    start_time=session_data['start_time'],
                    end_time=session_data['end_time'],
                    meeting_type=session_data['meeting_type'],
                    location=session_data.get('location')
                )
        except Exception as e:
            community.delete()
            raise serializers.ValidationError(f"Error creating sessions: {str(e)}")
        community.update_total_members()

        return community

    def update(self, instance, validated_data):
        social_media_data = validated_data.pop('social_media', None)
        sessions_data = validated_data.pop('sessions', None)

        old_community_lead = instance.community_lead
        old_co_lead = instance.co_lead
        old_secretary = instance.secretary

        new_community_lead = validated_data.pop('community_lead', old_community_lead)
        new_co_lead = validated_data.pop('co_lead', old_co_lead)
        new_secretary = validated_data.pop('secretary', old_secretary)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.community_lead = new_community_lead
        instance.co_lead = new_co_lead
        instance.secretary = new_secretary

        instance.save()

        try:
            if old_community_lead != new_community_lead:
                if old_community_lead:
                    ExecutiveMember.objects.filter(
                        user=old_community_lead,
                        community=instance,
                        position='LEAD'
                    ).delete()
                if new_community_lead:
                    ExecutiveMember.objects.get_or_create(
                        user=new_community_lead,
                        community=instance,
                        position='LEAD'
                    )
            if old_co_lead != new_co_lead:
                if old_co_lead:
                    ExecutiveMember.objects.filter(
                        user=old_co_lead,
                        community=instance,
                        position='CO_LEAD'
                    ).delete()
                if new_co_lead:
                    ExecutiveMember.objects.get_or_create(
                        user=new_co_lead,
                        community=instance,
                        position='CO_LEAD'
                    )
            if old_secretary != new_secretary:
                if old_secretary:
                    ExecutiveMember.objects.filter(
                        user=old_secretary,
                        community=instance,
                        position='SECRETARY'
                    ).delete()
                if new_secretary:
                    ExecutiveMember.objects.get_or_create(
                        user=new_secretary,
                        community=instance,
                        position='SECRETARY'
                    )

        except Exception as e:
            raise serializers.ValidationError(f"Error updating executives: {str(e)}")
        if social_media_data is not None:
            try:
                instance.social_media.clear()
                social_media_instances = []
                for sm_data in social_media_data:
                    sm_instance, created = Social_media.objects.get_or_create(
                        platform=sm_data['platform'],
                        url=sm_data['url']
                    )
                    social_media_instances.append(sm_instance)
                instance.social_media.set(social_media_instances)
            except Exception as e:
                raise serializers.ValidationError(f"Error updating social media: {str(e)}")
        if sessions_data is not None:
            try:
                instance.sessions.all().delete()
                for session_data in sessions_data:
                    CommunitySession.objects.create(
                        community=instance,
                        day=session_data['day'],
                        start_time=session_data['start_time'],
                        end_time=session_data['end_time'],
                        meeting_type=session_data['meeting_type'],
                        location=session_data.get('location')
                    )
            except Exception as e:
                raise serializers.ValidationError(f"Error updating sessions: {str(e)}")
        instance.update_total_members()

        return instance

class CommunityJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMember
        fields = ['community', 'name', 'email']