from rest_framework import serializers
from .models import Partner
import traceback
import boto3
import uuid
from django.conf import settings

# class PartnerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Partner
#         fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    logo_field = serializers.ImageField(write_only=True, required=False)  # To handle logo upload
    logo_url = serializers.URLField(read_only=True)  # To return the S3 URL
    
    class Meta:
        model = Partner
        fields = '__all__'
        extra_kwargs = {
            'logo': {'read_only': True}  # Make the original logo field read-only
        }
    
    def create(self, validated_data):
        logo_file = validated_data.pop('logo_field', None)
        print("Starting partner creation process...")
        print(f"Logo file is in validated_data: {logo_file}")
        
        partner_instance = Partner.objects.create(**validated_data)
        print(f"Partner instance created with ID: {partner_instance.id}")
        
        if logo_file:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
                filename = f"partner_logos/{uuid.uuid4()}_{logo_file.name}"
                print(f"Generated filename: {filename}")
                
                logo_file.seek(0)
                s3_client.upload_fileobj(
                    logo_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    filename,
                    ExtraArgs={'ContentType': logo_file.content_type}
                )
                print("S3 upload completed")
                
                s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
                print(f"Setting S3 URL: {s3_url}")
                
                partner_instance.logo = s3_url
                partner_instance.save()
            except Exception as e:
                print(f"Error uploading to S3: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise serializers.ValidationError(f"Failed to upload logo to S3: {str(e)}")
        
        return partner_instance
    
    def update(self, instance, validated_data):
        logo_file = validated_data.pop('logo_field', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if logo_file:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                filename = f"partner_logos/{uuid.uuid4()}_{logo_file.name}"
                
                logo_file.seek(0)
                s3_client.upload_fileobj(
                    logo_file,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    filename,
                    ExtraArgs={'ContentType': logo_file.content_type}
                )
                
                s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{filename}"
                instance.logo = s3_url
            except Exception as e:
                print(f"Error uploading to S3: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise serializers.ValidationError(f"Failed to upload logo to S3: {str(e)}")
        
        instance.save()
        return instance