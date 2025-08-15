from django.db import models

class Partner(models.Model):
    class PartnershipStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
    
    class PartnerType(models.TextChoices):
        TECH = "TECH", "Tech"
        ACADEMIC = "ACADEMIC", "Academic"
        COMMUNITY = "COMMUNITY", "Community"
        MEDIA = "MEDIA", "Media"
        CORPORATE = "CORPORATE", "Corporate"
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=PartnerType.choices)
    description = models.TextField()
    logo = models.URLField()  # This will store the S3 URL
    web_url = models.URLField()
    contact_email = models.EmailField()
    contact_person = models.CharField(max_length=255)
    linked_in = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    ongoing = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=PartnershipStatus.choices)
    scope = models.TextField()
    benefits = models.TextField()
    events_supported = models.TextField()
    resources = models.TextField()
    achievements = models.TextField()
    target_audience = models.TextField()
    
    def __str__(self):
        return self.name    