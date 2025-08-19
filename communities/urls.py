from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityProfileViewSet,
    JoinCommunityView,
    CommunityMembersView
)

router = DefaultRouter()
router.register(r'communities',CommunityProfileViewSet,basename='community')

community_list_create = CommunityProfileViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

community_detail = CommunityProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'update',
})

community_search = CommunityProfileViewSet.as_view({
    'get': 'search_by_name',
})

urlpatterns = [
    path('add-community/',community_list_create,name='add-community'),
    path('list-communities/',community_list_create,name='list-communities'),
    path('retrieve-community/<int:pk>/',community_detail,name='retrieve-community'),
    path('update-community/<int:pk>/',community_detail,name='update-community'),
    path('search-community/',community_search,name='search-community'),

    path('communities/<int:pk>/join/', JoinCommunityView.as_view(), name='join-community'),
    path('communities/<int:pk>/members/', CommunityMembersView.as_view(), name='community-members'),
]

urlpatterns +=router.urls
