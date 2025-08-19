from django.urls import path,include
from rest_framework_nested import routers
from .views import EventViewSet,EventRegistrationViewSet


router = routers.DefaultRouter()
router.register(r'events',EventViewSet,basename='events')
router.register('registrations',EventRegistrationViewSet,basename='registrations')

event_router = routers.NestedDefaultRouter(router,r'events',lookup='event')
event_router.register(r'registrations',EventRegistrationViewSet,basename='event-registration')


urlpatterns = [
    path('',include(router.urls)),
    path('',include(event_router.urls))
]
