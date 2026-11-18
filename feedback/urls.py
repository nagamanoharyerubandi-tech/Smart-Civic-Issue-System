from django.urls import path
from . import views

urlpatterns = [
    path('citizen/feedback/<int:complaint_id>/', views.citizen_submit_feedback, name='citizen_submit_feedback'),
    path('admin-portal/feedback/', views.admin_feedback_list, name='admin_feedback_list'),
]
