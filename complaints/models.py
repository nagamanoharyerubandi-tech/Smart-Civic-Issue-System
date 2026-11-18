from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-exclamation-triangle', help_text='Bootstrap icon class e.g. bi-trash3')
    color = models.CharField(max_length=30, default='#1e3a8a', help_text='Hex color code for tags & charts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Issue Category'
        verbose_name_plural = 'Issue Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    head_officer_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )

    reference_id = models.CharField(max_length=30, unique=True, editable=False, db_index=True)
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    photograph = models.ImageField(upload_to='complaints/%Y/%m/', blank=True, null=True)

    # Location details
    city = models.CharField(max_length=100, default='Metropolis')
    area = models.CharField(max_length=150, help_text='Ward, Locality, or Neighborhood')
    address = models.TextField(help_text='Street name, building, or specific spot')
    landmark = models.CharField(max_length=150, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Management details
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Submitted', db_index=True)
    assigned_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Duplicate detection
    is_duplicate = models.BooleanField(default=False)
    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates'
    )
    duplicate_flagged_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Civic Complaint'
        verbose_name_plural = 'Civic Complaints'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_id:
            now = timezone.now()
            # Generate unique reference like CIV-202611-AB12
            prefix = f"CIV-{now.strftime('%Y%m')}"
            unique_suffix = uuid.uuid4().hex[:6].upper()
            self.reference_id = f"{prefix}-{unique_suffix}"
            while Complaint.objects.filter(reference_id=self.reference_id).exists():
                unique_suffix = uuid.uuid4().hex[:6].upper()
                self.reference_id = f"{prefix}-{unique_suffix}"

        if self.status == 'Resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'Resolved':
            self.resolved_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.reference_id}] {self.title} - {self.status}"

    @property
    def is_cancellable(self):
        return self.status == 'Submitted'

    @property
    def status_badge_class(self):
        mapping = {
            'Submitted': 'bg-secondary',
            'Under Review': 'bg-info text-dark',
            'Assigned': 'bg-primary',
            'In Progress': 'bg-warning text-dark',
            'Resolved': 'bg-success',
            'Rejected': 'bg-danger',
        }
        return mapping.get(self.status, 'bg-secondary')

    @property
    def priority_badge_class(self):
        mapping = {
            'Low': 'bg-info text-dark',
            'Medium': 'bg-primary',
            'High': 'bg-danger',
        }
        return mapping.get(self.priority, 'bg-secondary')

    @property
    def progress_percentage(self):
        mapping = {
            'Submitted': 15,
            'Under Review': 35,
            'Assigned': 60,
            'In Progress': 80,
            'Resolved': 100,
            'Rejected': 100,
        }
        return mapping.get(self.status, 0)


class ComplaintAssignment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='assignments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_by_user')
    assigned_at = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField(blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default='Active')

    class Meta:
        verbose_name = 'Complaint Assignment'
        verbose_name_plural = 'Complaint Assignments'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.complaint.reference_id} -> {self.department.code}"


class ComplaintStatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=25)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='status_changes')
    remarks = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Status History Record'
        verbose_name_plural = 'Status History Records'
        ordering = ['changed_at']

    def __str__(self):
        return f"{self.complaint.reference_id} changed to {self.status} at {self.changed_at}"
