from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('admin', 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Metropolis')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_citizen(self):
        return self.role == 'citizen'

    @property
    def is_administrator(self):
        return self.role == 'admin' or self.user.is_staff or self.user.is_superuser


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if (instance.is_superuser or instance.is_staff) else 'citizen'
        Profile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            if instance.is_superuser or instance.is_staff:
                if instance.profile.role != 'admin':
                    instance.profile.role = 'admin'
                    instance.profile.save()
        else:
            role = 'admin' if (instance.is_superuser or instance.is_staff) else 'citizen'
            Profile.objects.create(user=instance, role=role)
