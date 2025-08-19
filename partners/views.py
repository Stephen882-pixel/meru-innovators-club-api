from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets,status
from .models import Partner
from .serializers import PartnerSerializer
from rest_framework.response import Response


class PartnerViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing partners of the platform.
    Supports CRUD operations:
    - List all partners
    - Retrieve a single partner by ID
    - Create a new partner
    - Update existing partner details
    - Delete a partner
    """
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="List all partners",
        operation_description="Retrieve a paginated list of all registered partners.",
        responses={200: PartnerSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="Retrieve a partner",
        operation_description="Retrieve details of a specific partner by their ID.",
        responses={200: PartnerSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="Create a new partner",
        operation_description="Add a new partner by providing the required details.",
        request_body=PartnerSerializer,
        responses={201: PartnerSerializer()},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="Update partner details",
        operation_description="Update the details of an existing partner. "
                              "Supports both PUT (full update) and PATCH (partial update).",
        request_body=PartnerSerializer,
        responses={200: PartnerSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="Partially update partner details",
        operation_description="Partially update one or more fields of an existing partner.",
        request_body=PartnerSerializer,
        responses={200: PartnerSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Partners"],
        operation_summary="Delete a partner",
        operation_description="Delete a partner by their ID. "
                              "Returns a success message confirming deletion.",
        responses={200: openapi.Response(
            description="Success message after deletion",
            examples={
                "application/json": {
                    "message": "Partner 'XYZ Ltd' has been successfully deleted."
                }
            }
        )}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        partner_name = instance.name  # Store the name before deletion
        self.perform_destroy(instance)
        return Response(
            {"message": f"Partner '{partner_name}' has been successfully deleted."},
            status=status.HTTP_200_OK
        )