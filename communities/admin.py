from django.contrib import admin
from .models import Community,CommunityMember,CommunityProfile,CommunitySession,Social_media

# Register your models here.
admin.site.register(CommunityProfile)
admin.site.register(CommunitySession)
admin.site.register(Community)
admin.site.register(CommunityMember)
admin.site.register(Social_media)
