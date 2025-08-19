import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Feedback, FeedbackStatus
from .models import FeedbackCategory

@receiver(post_save, sender=Feedback)
def create_github_issue(sender, instance, created, **kwargs):
    if created and hasattr(settings, 'GITHUB_REPO') and hasattr(settings, 'GITHUB_TOKEN'):
        if instance.category not in [FeedbackCategory.BUG_REPORT, 
                                     FeedbackCategory.FEATURE_REQUEST]:
            return


        labels = [instance.get_category_display()]
        if instance.priority:
            labels.append(f"Priority: {instance.get_priority_display()}")

        url = f"https://api.github.com/repos/{settings.GITHUB_REPO}/issues"
        headers = {
            'Authorization': f'token {settings.GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        issue_body = f"""
## Feedback from: {instance.email}

### Description
{instance.comment}

### Details
- Category: {instance.get_category_display()}
- Priority: {instance.get_priority_display() if instance.priority else 'Not set'}
- Rating: {instance.rating if instance.rating else 'Not provided'}
- Submitted: {instance.submitted_at}
- Feedback ID: {instance.id}


        """
        
        data = {
            'title': f"{instance.get_category_display()}: Feedback #{instance.id}",
            'body': issue_body,
            'labels': labels
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            issue_data = response.json()

            
        except requests.exceptions.RequestException as e:
            print(f"Error creating GitHub issue: {e}")

from django.core.mail import send_mail

@receiver(post_save, sender=Feedback)
def notify_status_change(sender, instance, created, **kwargs):
    if created:
        return

    if instance.tracker.has_changed('status') and instance.tracker.previous('status'):
        previous_status = dict(FeedbackStatus.choices).get(instance.tracker.previous('status'))
        current_status = instance.get_status_display()

        subject = f"Your feedback #{instance.id} status has been updated"
        message = f"""
Hello {instance.user.get_full_name() or instance.user.username},

The status of your feedback has been updated from "{previous_status}" to "{current_status}".

Feedback details:
- Category: {instance.get_category_display()}
- Comment: "{instance.comment[:100]}..."

Thank you for your feedback!
        """
        
        send_mail(
            subject,
            message,
            'noreply@yourdomain.com',
            [instance.email],
            fail_silently=False,
        )