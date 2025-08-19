from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets,permissions,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Testimonial
from django.db import models
from .serializers import TestimonialSerializer
from .permissions import IsAdminOrReadOnly,IsOwnerOrReadOnly


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing testimonials.

    Provides default actions:
    - **list**: Get all approved testimonials (staff users can see all).
    - **retrieve**: Get a single testimonial by ID.
    - **create**: Authenticated users can create testimonials.
    - **update/partial_update**: Owners can update their testimonials.
    - **destroy**: Owners can delete their testimonials.

    Custom admin actions:
    - **approve**: Mark a testimonial as approved.
    - **reject**: Mark a testimonial as rejected.
    """

    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        """
        Assigns permissions based on the action:
        - `update`, `partial_update`, `destroy`: Owner only.
        - `approve`, `reject`: Admin only.
        - `create`: Authenticated users.
        - `list`: Open to everyone.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action in ['approve', 'reject']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            permission_classes = []
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Controls queryset visibility:
        - Staff can see all testimonials.
        - Normal users see only approved testimonials.
        """
        queryset = Testimonial.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(status=Testimonial.APPROVED)


    @swagger_auto_schema(
        operation_summary="Approve a testimonial",
        operation_description="Mark the given testimonial as **approved**. Only admins can perform this action.",
        responses={200: openapi.Response("Testimonial approved successfully.")}
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        testimonial = self.get_object()
        testimonial.status = Testimonial.APPROVED
        testimonial.save()
        return Response({'status': 'testimonial approved'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Reject a testimonial",
        operation_description="Mark the given testimonial as **rejected**. Only admins can perform this action.",
        responses={200: openapi.Response("Testimonial rejected successfully.")}
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        testimonial = self.get_object()
        testimonial.status = Testimonial.REJECTED
        testimonial.save()
        return Response({'status': 'testimonial rejected'}, status=status.HTTP_200_OK)



    @swagger_auto_schema(
        operation_summary="List testimonials",
        operation_description="Retrieve a list of testimonials. "
                              "Normal users only see approved testimonials. "
                              "Staff users see all.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a testimonial",
        operation_description="Retrieve a single testimonial by ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a testimonial",
        operation_description="Authenticated users can create a testimonial. "
                              "New testimonials are pending approval by default.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a testimonial",
        operation_description="Update an existing testimonial. Only the testimonial owner can update it.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a testimonial",
        operation_description="Partially update fields of a testimonial. Only the testimonial owner can update it.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a testimonial",
        operation_description="Delete a testimonial. Only the testimonial owner can delete it.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


