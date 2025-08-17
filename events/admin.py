from django.contrib import admin
from .models import Events,EventRegistration


# Register your models here.

admin.site.register(Events)
admin.site.register(EventRegistration)