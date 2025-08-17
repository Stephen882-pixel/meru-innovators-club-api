from rest_framework import serializers
from .models import Events,EventRegistration
import boto3
from django.conf import settings
import uuid
from events.Email import send_ticket_email


class EventsSerializer(serializers.ModelSerializer):
    image_field = serializers.ImageField(write_only=True, required=False)  # Handle image upload
    image_url = serializers.SerializerMethodField()  # Return the S3 URL

    class Meta:
        model = Events
        fields = ['id', 'name', 'category', 'description',
                  'image_url', 'image_field', 'date', 'location',
                  'organizer', 'contact_email', 'is_virtual']
        extra_kwargs = {
            'image_url': {'read_only': True}  # Read-only field for S3 URL
        }

    def get_image_url(self, obj):
        """Return the full S3 URL for the image."""
        if obj.image_url:
            # Debug: Print what we're working with
            print(f"get_image_url processing: {obj.image_url}")

            if obj.image_url.startswith('http'):
                print(f"Using existing URL: {obj.image_url}")
                return obj.image_url  # Already a full URL

            full_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{obj.image_url}"
            print(f"Converted to full URL: {full_url}")
            return full_url
        return None

    def create(self, validated_data):
        # Extract image_field from the validated data
        image_file = validated_data.pop('image_field', None)
        print("Starting creating process....")
        print(f"Image file is in validated_data:{image_file}")
        # Create the event instance
        event_instance = Events.objects.create(**validated_data)
        print(f"Event instance created with ID: {event_instance.id}")


        # Handle S3 upload if an image is provided
        if image_file:
            try:
                print(f"Attempting S3 upload for file: {image_file.name}")

                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )

                # Generate a unique file name
                filename = f"event_images/{uuid.uuid4()}_{image_file.name}"
                print(f"Generated filename: {filename}")

                # Reset file pointer
                image_file.seek(0)

                # Upload the file to S3
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


                # store just the path,the SerializerMethodField will construct the full url
                event_instance.image_url = filename
                event_instance.save()


                # Set the public S3 URL in the image field
                # event_instance.image = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
                # event_instance.save()
            except Exception as e:
                print(f"Error uploading to S3: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                raise serializers.ValidationError(f"Failed to upload image to S3: {str(e)}")
        return event_instance



    def update(self, instance, validated_data):
        image_file = validated_data.pop('image_field', None)

        # Update other fields
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

                # Delete old image if it exists and isn't the default
                if instance.image_url and 'default.png' not in instance.image_url:
                    # Handle both path-only and full URL formats
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

                # Generate unique filename
                filename = f"event_images/{uuid.uuid4()}_{image_file.name}"
                image_file.seek(0)

                # Upload new image
                s3_client.upload_fileobj(
                    image_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    filename,
                    ExtraArgs={'ContentType': image_file.content_type}
                )

                # Store just the path, not the full URL (consistent with create method)
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

        # Send ticket email
        send_ticket_email(registration)

        return registration


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = ['name', 'description', 'location', 'date', 'category', 'organizer']


class MyRegistrationSerializer(serializers.ModelSerializer):
    # Include the event details
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

