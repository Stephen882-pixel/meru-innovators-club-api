from rest_framework import generics, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsOwnerOrReadOnly

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Assuming event_id is passed in the URL
        event_id = self.kwargs.get('event_id')
        return Comment.objects.filter(event_id=event_id, parent__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

class CommentReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Get replies for a specific comment via its ID in the URL
        parent_comment_id = self.kwargs.get('comment_id')
        return Comment.objects.filter(parent_id=parent_comment_id)

    def perform_create(self, serializer):
        parent = Comment.objects.get(id=self.kwargs.get('comment_id'))
        serializer.save(user=self.request.user, parent=parent, event=parent.event)