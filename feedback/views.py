from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets,permissions,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Feedback, FeedbackPriority, FeedbackStatus 
from .serializers import FeedbackCreateSerializer,FeedbackDetailSerializer
from django.db.models import Count

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-submitted_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'priority']
    search_fields = ['comment', 'email']
    ordering_fields = ['submitted_at', 'updated_at', 'priority']

    def get_serializer_class(self):
        if self.action == 'create':
            return FeedbackCreateSerializer
        return FeedbackDetailSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'set_priority', 'set_status']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Feedback.objects.all().order_by('-submitted_at')
        return Feedback.objects.filter(user=user).order_by('-submitted_at')

    @swagger_auto_schema(
        method="patch",
        operation_summary="Set feedback priority",
        operation_description="Allows admins to update the priority of a feedback entry.",
        tags=["Feedback"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "priority": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Priority of the feedback",
                    enum=[p[0] for p in FeedbackPriority.choices]
                )
            },
            required=["priority"]
        ),
        responses={
            200: openapi.Response("Priority successfully updated"),
            400: openapi.Response("Invalid priority value"),
        },
    )
    @action(detail=True, methods=['patch'])
    def set_priority(self, request, pk=None):
        feedback = self.get_object()
        priority = request.data.get('priority')
        if priority in dict(FeedbackPriority.choices):
            feedback.priority = priority
            feedback.save()
            return Response({'status': 'priority set'})
        return Response({'error': 'Invalid priority'}, status=400)

    @swagger_auto_schema(
        method="patch",
        operation_summary="Set feedback status",
        operation_description="Allows admins to update the status of a feedback entry.",
        tags=["Feedback"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Status of the feedback",
                    enum=[s[0] for s in FeedbackStatus.choices]
                )
            },
            required=["status"]
        ),
        responses={
            200: openapi.Response("Status successfully updated"),
            400: openapi.Response("Invalid status value"),
        },
    )
    @action(detail=True, methods=['patch'])
    def set_status(self, request, pk=None):
        feedback = self.get_object()
        status = request.data.get('status')
        if status in dict(FeedbackStatus.choices):
            feedback.status = status
            feedback.save()
            return Response({'status': 'status updated'})
        return Response({'error': 'Invalid status'}, status=400)

    @swagger_auto_schema(
        method="get",
        operation_summary="Feedback analytics",
        operation_description=(
                "Provides feedback analytics including category distribution, "
                "status distribution, priority distribution, and submission trends "
                "for the last 30 days."
        ),
        tags=["Feedback"],
        responses={
            200: openapi.Response(
                description="Analytics data retrieved successfully",
                examples={
                    "application/json": {
                        "category_stats": [{"category": "BUG_REPORT", "count": 5}],
                        "status_stats": [{"status": "PENDING", "count": 10}],
                        "priority_stats": [{"priority": "HIGH", "count": 3}],
                        "trend_data": [{"date": "2025-08-01", "count": 2}],
                        "total_count": 18,
                    }
                }
            )
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def analytics(self, request):
        # Get stats by category
        category_stats = Feedback.objects.values('category')\
            .annotate(count=Count('id'))\
            .order_by('-count')
        
        # Get stats by status
        status_stats = Feedback.objects.values('status')\
            .annotate(count=Count('id'))\
            .order_by('-count')
        
        # Get stats by priority
        priority_stats = Feedback.objects.values('priority')\
            .annotate(count=Count('id'))\
            .order_by('-count')
        
        # Get recent trend data
        from django.utils import timezone
        import datetime
        
        last_30_days = [timezone.now().date() - datetime.timedelta(days=x) for x in range(30)]
        last_30_days.reverse()
        
        trend_data = []
        for day in last_30_days:
            count = Feedback.objects.filter(
                submitted_at__date=day
            ).count()
            trend_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return Response({
            'category_stats': category_stats,
            'status_stats': status_stats,
            'priority_stats': priority_stats,
            'trend_data': trend_data,
            'total_count': Feedback.objects.count(),
        })
