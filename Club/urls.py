from django.urls import path
from .views import ClubDetailView, ExecutiveMemberViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'executives', ExecutiveMemberViewSet)

urlpatterns = [
    path('club/', ClubDetailView.as_view(), name='club-detail'),

]

urlpatterns += router.urls

