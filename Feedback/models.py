from django.db import models
from django.contrib.auth import get_user_model
from django.utils  import timezone
from model_utils import FieldTracker

User = get_user_model()

class FeedbackCategory(models.TextChoices):
    BUG_REPORT = 'BUG_REPORT', 'Bug Report'
    FEATURE_REQUEST = 'FEATURE_REQUEST', 'Feature Request'
    GENERAL_INQUIRY = 'GENERAL_INQUIRY', 'General Inquiry'
    ACCOUNT_ISSUE = 'ACCOUNT_ISSUE', 'Account Issue'
    PERFORMANCE_ISSUE = 'PERFORMANCE_ISSUE', 'Performance Issue'
    
class FeedbackStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    RESOLVED = 'RESOLVED', 'Resolved'

class FeedbackPriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True)
    email = models.EmailField(default='example@gmail.com')
    category = models.CharField(
        max_length=20,
        choices=FeedbackCategory.choices,
        default=FeedbackCategory.GENERAL_INQUIRY
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True, blank=True
    )
    comment = models.TextField()
    screenshot = models.ImageField(upload_to='feedback_screenshots/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=FeedbackStatus.choices,
        default=FeedbackStatus.PENDING
    )
    priority = models.CharField(
        max_length=20,
        choices=FeedbackPriority.choices,
        null=True, blank=True
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    tracker = FieldTracker(fields=['status', 'priority'])
    
    def __str__(self):
        return f"{self.category} - {self.user.username} - {self.submitted_at.strftime('%Y-%m-%d')}"
    

    



