from django.urls import path
from . import views

urlpatterns = [
    path('citizen/notifications/', views.notification_list, name='citizen_notifications'),
    path('admin-portal/notifications/', views.notification_list, name='admin_notifications'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),
]
