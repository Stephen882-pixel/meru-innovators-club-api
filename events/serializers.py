from rest_framework import serializers
from .models import Events,EventRegistration
import boto3
from django.conf import settings
import uuid
from events.Email import send_ticket_email


class EventsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Events
        fields = ['id', 'name', 'category', 'description',
                  'date', 'location',
                  'organizer', 'contact_email', 'is_virtual']




    def create(self, validated_data):
        print("Starting creating process....")

        event_instance = Events.objects.create(**validated_data)
        print(f"Event instance created with ID: {event_instance.id}")





    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['uid', 'event', 'full_name', 'email', 'course', 'educational_level',
                  'phone_number', 'expectations', 'registration_timestamp', 'ticket_number']
        read_only_fields = ['uid', 'registration_timestamp', 'ticket_number']

    def create(self, validated_data):
        registration = super().create(validated_data)


        send_ticket_email(registration)

        return registration


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = ['name', 'description', 'location', 'date', 'category', 'organizer']


class MyRegistrationSerializer(serializers.ModelSerializer):
    eventName = serializers.CharField(source='event.name')
    eventDescription = serializers.CharField(source='event.description')
    eventLocation = serializers.CharField(source='event.location')
    eventDate = serializers.DateTimeField(source='event.date')

    class Meta:
        model = EventRegistration
        fields = [
            'eventName', 'eventDescription', 'eventLocation', 'eventDate',
            'uid', 'event', 'full_name', 'email', 'course', 'educational_level',
            'phone_number', 'expectations', 'registration_timestamp', 'ticket_number'
        ]

