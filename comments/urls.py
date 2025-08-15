from django.urls import path
from .views import (
    CommentListCreateView,
    CommentDetailView,
    CommentReplyListCreateView
)

urlpatterns = [
    # List and create top-level comments for an event
    path('<int:event_id>/create/', CommentListCreateView.as_view(), name='comment-list-create'),
    # Retrieve, update, or delete a specific comment (or reply)
    path('<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    # List and create replies for a specific comment
    path('<int:comment_id>/replies/', CommentReplyListCreateView.as_view(), name='comment-replies'),
]