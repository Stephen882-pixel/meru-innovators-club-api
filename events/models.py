from django.db import models
from django.core.validators import EmailValidator
from account.models import User
import uuid

# Create your models here.
class Events(models.Model):
    CATEGORY_CHOICE = [
        ('WEB', 'Web Development'),
        ('CYBERSEC', 'Cyber Security'),
        ('ANDROID', 'Android Development'),
        ('AI', 'Artificial Intelligence'),
        ('BLOCKCHAIN', 'Blockchain'),
        ('IoT', 'Internate of Things'),
        ('CLOUD', 'Cloud Community')
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICE, null=False, default='Web Development')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(default="event_images/default.png",null=True)  # S3 image URL will be stored here
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.CharField(max_length=100)
    contact_email = models.EmailField(null=True, blank=True)
    is_virtual = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    EDUCATION_LEVELS = [
        ('1', 'Year 1'),
        ('2', 'Year 2'),
        ('3', 'Year 3'),
        ('4', 'Year 4'),
        ('5', 'Year 5'),
    ]

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations_events_app', null=True)
    event = models.ForeignKey('Events', on_delete=models.CASCADE, related_name='registrations')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    course = models.CharField(max_length=200)
    educational_level = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    expectations = models.CharField(max_length=100, null=True)
    registration_timestamp = models.DateTimeField(auto_now_add=True)
    ticket_number = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.full_name} - {self.event.name}"

    class Meta:
        unique_together = ['email', 'event']