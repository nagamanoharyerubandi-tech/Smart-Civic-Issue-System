"""
URL Configuration for SMART CIVIC ISSUE REPORTING & RESOLUTION MANAGEMENT SYSTEM
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Built-in Django Admin (Optional technical access)
    path('django-admin/', admin.site.urls),

    # App URLs
    path('', include('dashboard.urls')),
    path('', include('accounts.urls')),
    path('', include('complaints.urls')),
    path('', include('notifications.urls')),
    path('', include('feedback.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
