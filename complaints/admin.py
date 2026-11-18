from django.contrib import admin
from .models import Category, Department, Complaint, ComplaintAssignment, ComplaintStatusHistory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_officer_name', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'head_officer_name')


class ComplaintStatusHistoryInline(admin.TabularInline):
    model = ComplaintStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'remarks', 'changed_at')
    can_delete = False


class ComplaintAssignmentInline(admin.TabularInline):
    model = ComplaintAssignment
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'title', 'citizen', 'category', 'status', 'priority', 'assigned_department', 'created_at')
    list_filter = ('status', 'priority', 'category', 'assigned_department', 'city')
    search_fields = ('reference_id', 'title', 'description', 'area', 'address', 'citizen__username')
    readonly_fields = ('reference_id', 'created_at', 'updated_at')
    inlines = [ComplaintAssignmentInline, ComplaintStatusHistoryInline]


@admin.register(ComplaintAssignment)
class ComplaintAssignmentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'department', 'assigned_by', 'assigned_at', 'status')
    list_filter = ('department', 'status')


@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status', 'changed_by', 'changed_at')
    list_filter = ('status', 'changed_at')
