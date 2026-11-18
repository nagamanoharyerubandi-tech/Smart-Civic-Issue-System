from django.db import models
from django.contrib.auth.models import User
from complaints.models import Complaint


class Notification(models.Model):
    TYPE_CHOICES = (
        ('status_change', 'Status Change'),
        ('assignment', 'Department Assignment'),
        ('priority_change', 'Priority Change'),
        ('resolution', 'Issue Resolved'),
        ('feedback_request', 'Feedback Request'),
        ('duplicate_flag', 'Duplicate Complaint Alert'),
        ('general', 'General Notification'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    @property
    def icon_class(self):
        mapping = {
            'status_change': 'bi-arrow-repeat text-primary',
            'assignment': 'bi-building-gear text-info',
            'priority_change': 'bi-exclamation-diamond text-warning',
            'resolution': 'bi-check-circle-fill text-success',
            'feedback_request': 'bi-star text-warning',
            'duplicate_flag': 'bi-copy text-danger',
            'general': 'bi-bell text-secondary',
        }
        return mapping.get(self.notification_type, 'bi-bell text-secondary')
