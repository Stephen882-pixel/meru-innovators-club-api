from django.contrib import admin
from django.urls import path, include,re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from partners.views import PartnerViewSet
from Innovation_WebApp.views import (
    CommunityMembersView,
    CommunityProfileViewSet,
    JoinCommunityView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Meru University Science Innovators Club API",
        default_version="v1",
        description="API documentation for Meru University Science Innovators Club",
        contact=openapi.Contact(email="innovatorsmust@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)


from testimonials.views import TestimonialViewSet
router = DefaultRouter()
router.register(r'communities', CommunityProfileViewSet)
router.register(r'testimonials', TestimonialViewSet)
router.register(r'partners', PartnerViewSet)


community_viewset = CommunityProfileViewSet.as_view({
    'post':'create',
    'get':'list',
})

detail_viewset = CommunityProfileViewSet.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'update',
})

search_viewset = CommunityProfileViewSet.as_view({
    'get':'search_by_name',
})


urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),

    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc UI
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #path('', include('Innovation_WebApp.urls')),
    path('api/', include('Api.urls')),
    path('comments/', include('comments.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    

    path('add-community/', community_viewset, name='add-community'),
    path('list-communities/', community_viewset, name='list-communities'),
    path('retrieve-community/<int:pk>/', detail_viewset, name='retrieve-community'),
    path('update-community/<int:pk>/', detail_viewset, name='update-community'),
    path('search-community/', search_viewset, name='search-community'),
    path('communities/<int:pk>/join/', JoinCommunityView.as_view(), name='join-community'),
    path('communities/<int:pk>/members/', CommunityMembersView.as_view(), name='community_members'),
    path('', include(router.urls)),
    #path('', include(event_router.urls)),
    path('testimonies/', include('testimonials.urls')),
    path('', include('Feedback.urls')),
    path('comments/', include('comments.urls')),
    path('api/', include('Club.urls')),



    path('api/',include('events.urls')),
]

