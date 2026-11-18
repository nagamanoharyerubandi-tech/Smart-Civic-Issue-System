from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'citizen', 'rating', 'is_published', 'created_at')
    list_filter = ('rating', 'is_published', 'created_at')
    search_fields = ('complaint__reference_id', 'citizen__username', 'comments')
