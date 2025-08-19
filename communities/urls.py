from django.urls import path
from .views import (
    CommunityProfileViewSet,
    JoinCommunityView,
    CommunityMembersView
)

community_list = CommunityProfileViewSet.as_view({'get': 'list'})
community_create = CommunityProfileViewSet.as_view({'post': 'create'})
community_retrieve = CommunityProfileViewSet.as_view({'get': 'retrieve'})
community_update = CommunityProfileViewSet.as_view({'put': 'update', 'patch': 'update'})
community_search = CommunityProfileViewSet.as_view({'get': 'search_by_name'})

urlpatterns = [
    path('list-communities/', community_list, name='list-communities'),
    path('add-community/', community_create, name='add-community'),
    path('search-community/', community_search, name='search-community'),
    path('get-community/<int:pk>/', community_retrieve, name='get-community'),
    path('update-community/<int:pk>/', community_update, name='update-community'),


    path('join-community/<int:pk>/', JoinCommunityView.as_view(), name='join-community'),
    path('community-members/<int:pk>/', CommunityMembersView.as_view(), name='community-members'),
]

