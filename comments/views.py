from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsOwnerOrReadOnly


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Comment.objects.filter(event_id=event_id, parent__isnull=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="List all top-level comments for an event",
        operation_description="Retrieve all comments (without replies) associated with a given event.",
        tags=["Comments"],
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new comment on an event",
        operation_description="Post a new top-level comment under a specific event. Authentication required.",
        tags=["Comments"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING, example="This is a great event!"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Comment created successfully",
                schema=CommentSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "event": 5,
                        "user": 3,
                        "content": "This is a great event!",
                        "created_at": "2025-08-19T12:30:00Z",
                        "updated_at": "2025-08-19T12:30:00Z",
                        "parent": None
                    }
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Retrieve a comment",
        operation_description="Get the details of a specific comment by its ID.",
        tags=["Comments"],
        responses={200: CommentSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a comment",
        operation_description="Update the content of an existing comment. Only the owner can update.",
        tags=["Comments"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING, example="Updated comment content"),
            },
        ),
        responses={
            200: CommentSerializer,
            403: "Forbidden - not the owner",
            400: "Bad Request",
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a comment",
        operation_description="Partially update the content of a comment (PATCH).",
        tags=["Comments"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING, example="Partially updated comment"),
            },
        ),
        responses={200: CommentSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a comment",
        operation_description="Delete a specific comment. Only the owner can delete.",
        tags=["Comments"],
        responses={204: "No Content", 403: "Forbidden"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CommentReplyListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        parent_comment_id = self.kwargs.get('comment_id')
        return Comment.objects.filter(parent_id=parent_comment_id)

    def perform_create(self, serializer):
        parent = Comment.objects.get(id=self.kwargs.get('comment_id'))
        serializer.save(user=self.request.user, parent=parent, event=parent.event)

    @swagger_auto_schema(
        operation_summary="List replies to a comment",
        operation_description="Retrieve all replies associated with a specific parent comment.",
        tags=["Comment Replies"],
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Reply to a comment",
        operation_description="Post a reply under an existing comment. Authentication required.",
        tags=["Comment Replies"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING, example="Thanks for sharing your thoughts!"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Reply created successfully",
                schema=CommentSerializer,
                examples={
                    "application/json": {
                        "id": 10,
                        "event": 5,
                        "user": 3,
                        "content": "Thanks for sharing your thoughts!",
                        "created_at": "2025-08-19T12:45:00Z",
                        "updated_at": "2025-08-19T12:45:00Z",
                        "parent": 1
                    }
                },
            ),
            400: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
