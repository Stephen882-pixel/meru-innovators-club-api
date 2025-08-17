from rest_framework import serializers
from .models import Events,EventRegistration
import boto3
from django.conf import settings
import uuid
from events.Email import send_ticket_email


class EventsSerializer(serializers.ModelSerializer):
    image_field = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = ['id', 'name', 'category', 'description',
                  'image_url', 'image_field', 'date', 'location',
                  'organizer', 'contact_email', 'is_virtual']
        extra_kwargs = {
            'image_url': {'read_only': True}
        }

    def get_image_url(self, obj):
        if obj.image_url:
            print(f"get_image_url processing: {obj.image_url}")

            if obj.image_url.startswith('http'):
                print(f"Using existing URL: {obj.image_url}")
                return obj.image_url

            full_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{obj.image_url}"
            print(f"Converted to full URL: {full_url}")
            return full_url
        return None

    def create(self, validated_data):
        image_file = validated_data.pop('image_field', None)
        print("Starting creating process....")
        print(f"Image file is in validated_data:{image_file}")

        event_instance = Events.objects.create(**validated_data)
        print(f"Event instance created with ID: {event_instance.id}")

        if image_file:
            try:
                print(f"Attempting S3 upload for file: {image_file.name}")
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                filename = f"event_images/{uuid.uuid4()}_{image_file.name}"
                print(f"Generated filename: {filename}")
                image_file.seek(0)
                print("Starting S3 upload...")
                s3_client.upload_fileobj(
                    image_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    filename,
                    ExtraArgs={
                        'ContentType': image_file.content_type
                    }
                )
                print("S3 upload completed")
                event_instance.image_url = filename
                event_instance.save()
            except Exception as e:
                print(f"Error uploading to S3: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise serializers.ValidationError(f"Failed to upload image to S3: {str(e)}")
        return event_instance



    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_field', None)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image_file:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )


                if instance.image_url and 'default.png' not in instance.image_url:
                    old_key = instance.image_url
                    if instance.image_url.startswith('http'):
                        old_key = instance.image_url.split('.com/')[-1]

                    try:
                        s3_client.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=old_key
                        )
                    except Exception as e:
                        print(f"Warning: Failed to delete old image: {str(e)}")

                filename = f"event_images/{uuid.uuid4()}_{image_file.name}"
                image_file.seek(0)
                s3_client.upload_fileobj(
                    image_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    filename,
                    ExtraArgs={'ContentType': image_file.content_type}
                )
                instance.image_url = filename
            except Exception as e:
                print(f"Error uploading to S3: {str(e)}")
                raise serializers.ValidationError(f"Failed to upload image to S3: {str(e)}")

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

