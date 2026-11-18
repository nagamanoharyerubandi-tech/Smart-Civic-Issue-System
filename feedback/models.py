from django.db import models
from django.contrib.auth.models import User
from complaints.models import Complaint
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    comments = models.TextField(help_text='Citizen review & resolution feedback')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Citizen Feedback'
        verbose_name_plural = 'Citizen Feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.complaint.reference_id} - {self.rating} Stars"

    @property
    def stars_range(self):
        return range(self.rating)

    @property
    def empty_stars_range(self):
        return range(5 - self.rating)
