from rest_framework import serializers
from .models import SubscribedUsers


import logging

logger = logging.getLogger(__name__)

class SubscribedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribedUsers
        fields = ['id', 'email', 'created_date']


