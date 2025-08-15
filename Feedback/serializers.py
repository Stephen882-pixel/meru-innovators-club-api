from rest_framework import serializers
from .models import Feedback

class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['category','rating','comment','screenshot']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user   
        validated_data['email'] = user.email    
        validated_data['status'] = 'PENDING'
        return super().create(validated_data)
    
class FeedbackDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display',read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_name', 'email', 'category', 'category_display', 
            'rating', 'comment', 'screenshot', 'status', 'status_display', 
            'priority', 'priority_display', 'submitted_at', 'updated_at'
        ]
        read_only_fields = ['user', 'email', 'submitted_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    