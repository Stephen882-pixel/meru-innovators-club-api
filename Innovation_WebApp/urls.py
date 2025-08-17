from django.urls import path
from . import views

urlpatterns = [
    path('newsletter/', views.NewsletterSendView.as_view(), name='newsletter'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]



