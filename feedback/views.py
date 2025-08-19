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

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="List feedback entries",
        operation_description="Retrieve all feedback entries. Admins see all, while regular users only see their own.",
        responses={
            200: openapi.Response(
                description="List of feedback entries",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user": 5,
                            "email": "john@example.com",
                            "comment": "The app keeps crashing on login.",
                            "category": "BUG_REPORT",
                            "status": "PENDING",
                            "priority": "HIGH",
                            "submitted_at": "2025-08-10T12:45:00Z",
                            "updated_at": "2025-08-15T09:30:00Z"
                        }
                    ]
                }
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="Retrieve a feedback entry",
        operation_description="Get details of a specific feedback entry by ID.",
        responses={
            200: openapi.Response(
                description="Feedback entry details",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 5,
                        "email": "john@example.com",
                        "comment": "The app keeps crashing on login.",
                        "category": "BUG_REPORT",
                        "status": "PENDING",
                        "priority": "HIGH",
                        "submitted_at": "2025-08-10T12:45:00Z",
                        "updated_at": "2025-08-15T09:30:00Z"
                    }
                }
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="Create new feedback",
        operation_description="Submit a new feedback entry. Requires authentication.",
        request_body=FeedbackCreateSerializer,
        responses={
            201: openapi.Response(
                description="Feedback successfully created",
                examples={
                    "application/json": {
                        "id": 2,
                        "user": 5,
                        "email": "jane@example.com",
                        "comment": "Would love to see dark mode.",
                        "category": "FEATURE_REQUEST",
                        "status": "PENDING",
                        "priority": "MEDIUM",
                        "submitted_at": "2025-08-18T08:20:00Z",
                        "updated_at": "2025-08-18T08:20:00Z"
                    }
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="Update feedback entry",
        operation_description="Admins can update existing feedback entries fully or partially.",
        request_body=FeedbackDetailSerializer,
        responses={
            200: openapi.Response(
                description="Feedback entry updated",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 5,
                        "email": "john@example.com",
                        "comment": "The crash issue seems fixed now.",
                        "category": "BUG_REPORT",
                        "status": "RESOLVED",
                        "priority": "LOW",
                        "submitted_at": "2025-08-10T12:45:00Z",
                        "updated_at": "2025-08-19T11:00:00Z"
                    }
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="Partially update a feedback entry",
        operation_description="Admins can partially update specific fields of a feedback entry. "
                              "For example, updating only the status or priority without changing other fields.",
        request_body=FeedbackDetailSerializer,
        responses={
            200: openapi.Response(
                description="Feedback entry partially updated",
                examples={
                    "application/json": {
                        "id": 1,
                        "status": "IN_PROGRESS",
                        "updated_at": "2025-08-19T14:22:00Z"
                    }
                }
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Feedback"],
        operation_summary="Delete a feedback entry",
        operation_description="Admins can delete a feedback entry permanently. This action is irreversible.",
        responses={
            204: openapi.Response(
                description="Feedback entry successfully deleted",
                examples={"application/json": {"detail": "Feedback entry successfully deleted"}}
            ),
            404: openapi.Response(
                description="Feedback entry not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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
                    enum=[p[0] for p in FeedbackPriority.choices],
                    example="HIGH"
                )
            },
            required=["priority"]
        ),
        responses={
            200: openapi.Response(
                description="Priority successfully updated",
                examples={"application/json": {"status": "priority set"}}
            ),
            400: openapi.Response(
                description="Invalid priority value",
                examples={"application/json": {"error": "Invalid priority"}}
            ),
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
                    enum=[s[0] for s in FeedbackStatus.choices],
                    example="IN_PROGRESS"
                )
            },
            required=["status"]
        ),
        responses={
            200: openapi.Response(
                description="Status successfully updated",
                examples={"application/json": {"status": "status updated"}}
            ),
            400: openapi.Response(
                description="Invalid status value",
                examples={"application/json": {"error": "Invalid status"}}
            ),
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
                        "category_stats": [
                            {"category": "BUG_REPORT", "count": 5},
                            {"category": "FEATURE_REQUEST", "count": 3}
                        ],
                        "status_stats": [
                            {"status": "PENDING", "count": 10},
                            {"status": "RESOLVED", "count": 4}
                        ],
                        "priority_stats": [
                            {"priority": "HIGH", "count": 3},
                            {"priority": "LOW", "count": 7}
                        ],
                        "trend_data": [
                            {"date": "2025-08-01", "count": 2},
                            {"date": "2025-08-02", "count": 1},
                            {"date": "2025-08-03", "count": 0}
                        ],
                        "total_count": 18,
                    }
                }
            )
        },
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def analytics(self, request):
        category_stats = Feedback.objects.values('category')\
            .annotate(count=Count('id'))\
            .order_by('-count')

        status_stats = Feedback.objects.values('status')\
            .annotate(count=Count('id'))\
            .order_by('-count')

        priority_stats = Feedback.objects.values('priority')\
            .annotate(count=Count('id'))\
            .order_by('-count')

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

