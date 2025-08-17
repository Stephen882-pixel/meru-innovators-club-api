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
router.register(r'testimonials', TestimonialViewSet)
router.register(r'partners', PartnerViewSet)




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
    

    path('', include(router.urls)),
    #path('', include(event_router.urls)),
    path('testimonies/', include('testimonials.urls')),
    path('', include('Feedback.urls')),
    path('comments/', include('comments.urls')),



    path('api/', include('Club.urls')),
    path('api/',include('events.urls')),
    path('api/',include('communities.urls')),
]

