from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.public_home, name='home'),
    path('about/', views.public_about, name='about'),
    path('how-it-works/', views.public_how_it_works, name='how_it_works'),
    path('contact/', views.public_contact, name='contact'),
    path('track/', views.public_track_complaint, name='public_track'),

    # Citizen Dashboard
    path('citizen/dashboard/', views.citizen_dashboard, name='citizen_dashboard'),

    # Admin Dashboard & Analytics
    path('admin-portal/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/analytics/', views.admin_analytics, name='admin_analytics'),
    path('api/dashboard-charts/', views.api_dashboard_charts, name='api_dashboard_charts'),
]
