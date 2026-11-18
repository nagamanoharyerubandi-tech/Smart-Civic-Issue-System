from django.urls import path
from . import views

urlpatterns = [
    # Citizen routes
    path('citizen/complaints/', views.citizen_complaint_list, name='citizen_complaint_list'),
    path('citizen/complaints/create/', views.citizen_complaint_create, name='citizen_complaint_create'),
    path('citizen/complaints/<int:complaint_id>/', views.citizen_complaint_detail, name='citizen_complaint_detail'),
    path('citizen/complaints/<int:complaint_id>/cancel/', views.citizen_complaint_cancel, name='citizen_complaint_cancel'),
    path('citizen/complaints/<int:complaint_id>/track/', views.citizen_complaint_track, name='citizen_complaint_track'),

    # Admin routes
    path('admin-portal/complaints/', views.admin_complaint_list, name='admin_complaint_list'),
    path('admin-portal/complaints/<int:complaint_id>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin-portal/complaints/<int:complaint_id>/verify-duplicate/', views.admin_verify_duplicate, name='admin_verify_duplicate'),

    # Admin categories
    path('admin-portal/categories/', views.admin_category_list, name='admin_category_list'),
    path('admin-portal/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin-portal/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin-portal/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),

    # Admin departments
    path('admin-portal/departments/', views.admin_department_list, name='admin_department_list'),
    path('admin-portal/departments/create/', views.admin_department_create, name='admin_department_create'),
    path('admin-portal/departments/<int:department_id>/edit/', views.admin_department_edit, name='admin_department_edit'),
    path('admin-portal/departments/<int:department_id>/delete/', views.admin_department_delete, name='admin_department_delete'),

    # Admin citizens
    path('admin-portal/citizens/', views.admin_citizen_list, name='admin_citizen_list'),
]
