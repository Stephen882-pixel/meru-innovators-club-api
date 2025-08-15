from rest_framework import viewsets,status
from .models import Partner
from .serializers import PartnerSerializer
from rest_framework.response import Response

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        partner_name = instance.name  # Store the name before deletion
        self.perform_destroy(instance)
        return Response(
            {"message": f"Partner '{partner_name}' has been successfully deleted."},
            status=status.HTTP_200_OK
        )
