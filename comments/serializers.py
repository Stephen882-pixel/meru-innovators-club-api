from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # Nested replies. This will show replies for each comment.
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'event', 'content', 'created_at', 'parent', 'replies']
        read_only_fields = ['user', 'created_at', 'replies']

    def get_replies(self, obj):
        # You might want to limit recursion depth in a production system.
        serializer = CommentSerializer(obj.replies.all(), many=True, context=self.context)
        return serializer.data
    
    