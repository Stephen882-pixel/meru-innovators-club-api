from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Testimonial(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'), 
        (REJECTED, 'Rejected')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='testimonials')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.user.username} - {self.status}"
    