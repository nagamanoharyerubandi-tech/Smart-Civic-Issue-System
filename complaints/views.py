from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
from accounts.decorators import citizen_required, admin_required
from .models import Complaint, Category, Department, ComplaintAssignment, ComplaintStatusHistory
from .forms import (
    ComplaintSubmitForm, ComplaintStatusUpdateForm, ComplaintAssignDepartmentForm,
    CategoryForm, DepartmentForm
)
from .utils import detect_potential_duplicates
from notifications.utils import send_civic_notification


# ==============================================================================
# CITIZEN VIEWS
# ==============================================================================

@login_required
@citizen_required
def citizen_complaint_list(request):
    """
    Displays list of complaints submitted exclusively by the logged-in citizen.
    Supports status filtering and search.
    """
    status_filter = request.GET.get('status', '').strip()
    search_query = request.GET.get('q', '').strip()

    complaints_qs = Complaint.objects.filter(citizen=request.user).select_related(
        'category', 'assigned_department'
    ).order_by('-created_at')

    if status_filter:
        complaints_qs = complaints_qs.filter(status=status_filter)

    if search_query:
        complaints_qs = complaints_qs.filter(
            Q(reference_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    paginator = Paginator(complaints_qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Status counts for quick filter pills
    status_counts = {
        'all': Complaint.objects.filter(citizen=request.user).count(),
        'Submitted': Complaint.objects.filter(citizen=request.user, status='Submitted').count(),
        'In_Progress': Complaint.objects.filter(citizen=request.user, status__in=['Assigned', 'In Progress', 'Under Review']).count(),
        'Resolved': Complaint.objects.filter(citizen=request.user, status='Resolved').count(),
        'Rejected': Complaint.objects.filter(citizen=request.user, status='Rejected').count(),
    }

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_counts': status_counts,
        'status_choices': Complaint.STATUS_CHOICES,
    }
    return render(request, 'citizen/complaint_list.html', context)


@login_required
@citizen_required
def citizen_complaint_create(request):
    """
    Submits a new civic complaint with photograph upload and location details.
    Runs automated duplicate detection to flag potential overlaps for administrators.
    """
    if request.method == 'POST':
        form = ComplaintSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            complaint.status = 'Submitted'
            complaint.priority = 'Medium'
            complaint.save()

            # Record initial status in history
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                status='Submitted',
                changed_by=request.user,
                remarks='Complaint lodged by citizen via web portal.'
            )

            # Automated Duplicate Detection Check
            potential_duplicates = detect_potential_duplicates(
                category=complaint.category,
                city=complaint.city,
                area=complaint.area,
                address=complaint.address,
                exclude_id=complaint.id
            )

            if potential_duplicates.exists():
                first_match = potential_duplicates.first()
                complaint.is_duplicate = True
                complaint.duplicate_of = first_match
                complaint.duplicate_flagged_at = timezone.now()
                complaint.save()

                # Alert all active administrators about potential duplicate
                for admin in User.objects.filter(is_staff=True):
                    send_civic_notification(
                        recipient=admin,
                        title=f"Potential Duplicate Detected: {complaint.reference_id}",
                        message=f"New complaint in {complaint.area} matches existing issue {first_match.reference_id}.",
                        notification_type='duplicate_flag',
                        complaint=complaint,
                        action_url=f"/admin-portal/complaints/{complaint.id}/"
                    )

            # Send confirmation notification to citizen
            send_civic_notification(
                recipient=request.user,
                title=f"Complaint Lodged: {complaint.reference_id}",
                message=f"Your complaint '{complaint.title}' has been registered. Reference: {complaint.reference_id}.",
                notification_type='status_change',
                complaint=complaint,
                action_url=f"/citizen/complaints/{complaint.id}/"
            )

            # Alert administrators about new complaint
            for admin in User.objects.filter(is_staff=True):
                send_civic_notification(
                    recipient=admin,
                    title=f"New Complaint: {complaint.reference_id}",
                    message=f"Category: {complaint.category.name} in {complaint.area}.",
                    notification_type='status_change',
                    complaint=complaint,
                    action_url=f"/admin-portal/complaints/{complaint.id}/"
                )

            messages.success(
                request,
                f"Complaint #{complaint.reference_id} submitted successfully! You can track its live progress here."
            )
            return redirect('citizen_complaint_detail', complaint_id=complaint.id)
        else:
            messages.error(request, "Please correct the errors in the submission form.")
    else:
        form = ComplaintSubmitForm(initial={
            'city': request.user.profile.city or 'Metropolis City',
            'address': request.user.profile.address or ''
        })

    categories = Category.objects.filter(is_active=True)
    return render(request, 'citizen/complaint_create.html', {
        'form': form,
        'categories': categories
    })


@login_required
@citizen_required
def citizen_complaint_detail(request, complaint_id):
    """
    Displays full details of a complaint filed by the citizen.
    Includes visual status timeline, assignment details, and resolution notes.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('category', 'assigned_department', 'citizen'),
        id=complaint_id,
        citizen=request.user
    )
    status_history = complaint.status_history.select_related('changed_by').order_by('changed_at')
    assignments = complaint.assignments.select_related('department', 'assigned_by').order_by('-assigned_at')
    feedback = getattr(complaint, 'feedback', None)

    context = {
        'complaint': complaint,
        'status_history': status_history,
        'assignments': assignments,
        'feedback': feedback,
    }
    return render(request, 'citizen/complaint_detail.html', context)


@login_required
@citizen_required
def citizen_complaint_cancel(request, complaint_id):
    """
    Allows a citizen to cancel their own complaint IF it is still in 'Submitted' status.
    """
    complaint = get_object_or_404(Complaint, id=complaint_id, citizen=request.user)

    if not complaint.is_cancellable:
        messages.error(request, "This complaint has already entered administrative processing and cannot be cancelled.")
        return redirect('citizen_complaint_detail', complaint_id=complaint.id)

    if request.method == 'POST':
        cancellation_reason = request.POST.get('reason', 'Cancelled by citizen.')
        complaint.status = 'Rejected'
        complaint.resolution_notes = f"Cancelled by Citizen: {cancellation_reason}"
        complaint.save()

        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            status='Rejected',
            changed_by=request.user,
            remarks=f"Cancelled by Citizen. Reason: {cancellation_reason}"
        )

        send_civic_notification(
            recipient=request.user,
            title=f"Complaint Cancelled: {complaint.reference_id}",
            message=f"Your complaint #{complaint.reference_id} was successfully cancelled.",
            notification_type='status_change',
            complaint=complaint,
            action_url=f"/citizen/complaints/{complaint.id}/"
        )

        messages.info(request, f"Complaint #{complaint.reference_id} has been cancelled.")
        return redirect('citizen_complaint_list')

    return render(request, 'citizen/complaint_cancel_confirm.html', {'complaint': complaint})


@login_required
@citizen_required
def citizen_complaint_track(request, complaint_id):
    """
    Dedicated visual tracking page for a citizen complaint.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('category', 'assigned_department'),
        id=complaint_id,
        citizen=request.user
    )
    status_history = complaint.status_history.order_by('changed_at')
    return render(request, 'citizen/track_complaint.html', {
        'complaint': complaint,
        'status_history': status_history
    })


# ==============================================================================
# ADMINISTRATOR VIEWS
# ==============================================================================

@login_required
@admin_required
def admin_complaint_list(request):
    """
    Comprehensive administrative complaint management console.
    Provides multi-attribute search and filtering across all civic issues.
    """
    status_filter = request.GET.get('status', '').strip()
    priority_filter = request.GET.get('priority', '').strip()
    category_filter = request.GET.get('category', '').strip()
    department_filter = request.GET.get('department', '').strip()
    duplicate_filter = request.GET.get('duplicate', '').strip()
    search_query = request.GET.get('q', '').strip()

    complaints_qs = Complaint.objects.select_related(
        'citizen', 'category', 'assigned_department'
    ).order_by('-created_at')

    if status_filter:
        complaints_qs = complaints_qs.filter(status=status_filter)
    if priority_filter:
        complaints_qs = complaints_qs.filter(priority=priority_filter)
    if category_filter:
        complaints_qs = complaints_qs.filter(category_id=category_filter)
    if department_filter:
        complaints_qs = complaints_qs.filter(assigned_department_id=department_filter)
    if duplicate_filter == 'yes':
        complaints_qs = complaints_qs.filter(is_duplicate=True)
    if search_query:
        complaints_qs = complaints_qs.filter(
            Q(reference_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(citizen__username__icontains=search_query) |
            Q(citizen__first_name__icontains=search_query) |
            Q(citizen__last_name__icontains=search_query) |
            Q(area__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    paginator = Paginator(complaints_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)

    # Status counts for dashboard badges
    counts = {
        'total': Complaint.objects.count(),
        'submitted': Complaint.objects.filter(status='Submitted').count(),
        'review': Complaint.objects.filter(status='Under Review').count(),
        'assigned': Complaint.objects.filter(status='Assigned').count(),
        'in_progress': Complaint.objects.filter(status='In Progress').count(),
        'resolved': Complaint.objects.filter(status='Resolved').count(),
        'rejected': Complaint.objects.filter(status='Rejected').count(),
        'duplicates': Complaint.objects.filter(is_duplicate=True).count(),
    }

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'department_filter': department_filter,
        'duplicate_filter': duplicate_filter,
        'search_query': search_query,
        'categories': categories,
        'departments': departments,
        'counts': counts,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    }
    return render(request, 'admin_portal/complaint_list.html', context)


@login_required
@admin_required
def admin_complaint_detail(request, complaint_id):
    """
    Detailed administrative inspector and management console for a single complaint.
    Allows:
    - Status updates with audit remarks
    - Priority reclassification
    - Department dispatch and reassignment
    - Duplicate inspection and linkage
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('citizen', 'category', 'assigned_department', 'duplicate_of'),
        id=complaint_id
    )
    status_history = complaint.status_history.select_related('changed_by').order_by('-changed_at')
    assignments = complaint.assignments.select_related('department', 'assigned_by').order_by('-assigned_at')
    feedback = getattr(complaint, 'feedback', None)

    # Check for potential duplicates if not already linked
    potential_duplicates = detect_potential_duplicates(
        category=complaint.category,
        city=complaint.city,
        area=complaint.area,
        address=complaint.address,
        exclude_id=complaint.id
    )

    status_form = ComplaintStatusUpdateForm(initial={
        'status': complaint.status,
        'priority': complaint.priority,
    })
    assign_form = ComplaintAssignDepartmentForm(initial={
        'department': complaint.assigned_department
    })

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        # 1. Status and Priority Update
        if action_type == 'update_status':
            status_form = ComplaintStatusUpdateForm(request.POST)
            if status_form.is_valid():
                new_status = status_form.cleaned_data['status']
                new_priority = status_form.cleaned_data['priority']
                remarks = status_form.cleaned_data['remarks']

                old_status = complaint.status
                old_priority = complaint.priority

                complaint.status = new_status
                complaint.priority = new_priority
                if new_status == 'Resolved':
                    complaint.resolution_notes = remarks
                    complaint.resolved_at = timezone.now()
                elif new_status == 'Rejected':
                    complaint.resolution_notes = remarks
                complaint.save()

                # Add history entry
                history_remarks = remarks
                if old_priority != new_priority:
                    history_remarks += f" [Priority changed from {old_priority} to {new_priority}]"

                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status=new_status,
                    changed_by=request.user,
                    remarks=history_remarks
                )

                # Send Citizen Notification
                notif_type = 'resolution' if new_status == 'Resolved' else 'status_change'
                send_civic_notification(
                    recipient=complaint.citizen,
                    title=f"Status Updated: {complaint.reference_id} is now '{new_status}'",
                    message=f"Remarks: {remarks}",
                    notification_type=notif_type,
                    complaint=complaint,
                    action_url=f"/citizen/complaints/{complaint.id}/"
                )

                messages.success(request, f"Complaint status updated to '{new_status}' successfully.")
                return redirect('admin_complaint_detail', complaint_id=complaint.id)

        # 2. Department Assignment
        elif action_type == 'assign_department':
            assign_form = ComplaintAssignDepartmentForm(request.POST)
            if assign_form.is_valid():
                department = assign_form.cleaned_data['department']
                instructions = assign_form.cleaned_data['instructions']
                target_date = assign_form.cleaned_data['target_completion_date']

                complaint.assigned_department = department
                if complaint.status in ['Submitted', 'Under Review']:
                    complaint.status = 'Assigned'
                complaint.save()

                # Create assignment record
                ComplaintAssignment.objects.create(
                    complaint=complaint,
                    department=department,
                    assigned_by=request.user,
                    instructions=instructions,
                    target_completion_date=target_date,
                    status='Active'
                )

                # Record status change
                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    status='Assigned',
                    changed_by=request.user,
                    remarks=f"Assigned to {department.name}. Instructions: {instructions or 'Standard resolution procedure.'}"
                )

                # Notify Citizen
                send_civic_notification(
                    recipient=complaint.citizen,
                    title=f"Department Assigned: {complaint.reference_id}",
                    message=f"Your complaint has been assigned to {department.name} for technical field resolution.",
                    notification_type='assignment',
                    complaint=complaint,
                    action_url=f"/citizen/complaints/{complaint.id}/"
                )

                messages.success(request, f"Complaint assigned to {department.name} successfully.")
                return redirect('admin_complaint_detail', complaint_id=complaint.id)

    context = {
        'complaint': complaint,
        'status_history': status_history,
        'assignments': assignments,
        'feedback': feedback,
        'status_form': status_form,
        'assign_form': assign_form,
        'potential_duplicates': potential_duplicates,
    }
    return render(request, 'admin_portal/complaint_detail.html', context)


@login_required
@admin_required
def admin_verify_duplicate(request, complaint_id):
    """
    Handles administrator verification of duplicate complaints.
    Can link to existing complaint and mark as duplicate, or clear false alarm.
    """
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'mark_duplicate':
            primary_id = request.POST.get('primary_complaint_id')
            primary_complaint = get_object_or_404(Complaint, id=primary_id)

            complaint.is_duplicate = True
            complaint.duplicate_of = primary_complaint
            complaint.duplicate_flagged_at = timezone.now()
            complaint.status = 'Rejected'
            complaint.resolution_notes = f"Marked as duplicate of existing complaint #{primary_complaint.reference_id}."
            complaint.save()

            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                status='Rejected',
                changed_by=request.user,
                remarks=f"Marked as duplicate of #{primary_complaint.reference_id} and consolidated."
            )

            send_civic_notification(
                recipient=complaint.citizen,
                title=f"Complaint Consolidated: {complaint.reference_id}",
                message=f"Your complaint has been identified as a duplicate of active complaint #{primary_complaint.reference_id}. Both will be tracked together.",
                notification_type='status_change',
                complaint=complaint,
                action_url=f"/citizen/complaints/{complaint.id}/"
            )

            messages.info(request, f"Complaint #{complaint.reference_id} marked as duplicate of #{primary_complaint.reference_id}.")

        elif action == 'dismiss_duplicate':
            complaint.is_duplicate = False
            complaint.duplicate_of = None
            complaint.save()

            messages.success(request, f"Duplicate warning dismissed for #{complaint.reference_id}. Marked as distinct unique issue.")

    return redirect('admin_complaint_detail', complaint_id=complaint.id)


# ==============================================================================
# CATEGORY MANAGEMENT
# ==============================================================================

@login_required
@admin_required
def admin_category_list(request):
    categories = Category.objects.annotate(total_complaints=Count('complaints')).order_by('name')
    return render(request, 'admin_portal/category_list.html', {'categories': categories})


@login_required
@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created successfully.")
            return redirect('admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_portal/category_form.html', {'form': form, 'title': 'Create Issue Category'})


@login_required
@admin_required
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully.")
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_portal/category_form.html', {'form': form, 'title': f'Edit Category: {category.name}'})


@login_required
@admin_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if category.complaints.exists():
        messages.error(request, f"Cannot delete category '{category.name}' because active complaints are associated with it. You can deactivate it instead.")
        return redirect('admin_category_list')

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' was deleted.")
        return redirect('admin_category_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Category: {category.name}",
        'cancel_url': 'admin_category_list'
    })


# ==============================================================================
# DEPARTMENT MANAGEMENT
# ==============================================================================

@login_required
@admin_required
def admin_department_list(request):
    departments = Department.objects.annotate(
        total_assigned=Count('assigned_complaints'),
        resolved_count=Count('assigned_complaints', filter=Q(assigned_complaints__status='Resolved'))
    ).order_by('name')
    return render(request, 'admin_portal/department_list.html', {'departments': departments})


@login_required
@admin_required
def admin_department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully.")
            return redirect('admin_department_list')
    else:
        form = DepartmentForm()
    return render(request, 'admin_portal/department_form.html', {'form': form, 'title': 'Create Municipal Department'})


@login_required
@admin_required
def admin_department_edit(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{department.name}' updated successfully.")
            return redirect('admin_department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'admin_portal/department_form.html', {'form': form, 'title': f'Edit Department: {department.name}'})


@login_required
@admin_required
def admin_department_delete(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if department.assigned_complaints.exists():
        messages.error(request, f"Cannot delete department '{department.name}' as it has assigned complaints. You can mark it inactive instead.")
        return redirect('admin_department_list')

    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' was deleted.")
        return redirect('admin_department_list')

    return render(request, 'admin_portal/confirm_delete.html', {
        'object_name': f"Department: {department.name}",
        'cancel_url': 'admin_department_list'
    })


# ==============================================================================
# CITIZEN MANAGEMENT (ADMIN)
# ==============================================================================

@login_required
@admin_required
def admin_citizen_list(request):
    """
    Displays all registered citizens with their contact details, registration date,
    total complaints lodged, and active status toggle.
    """
    search_query = request.GET.get('q', '').strip()
    citizens_qs = User.objects.filter(is_staff=False, is_superuser=False).select_related('profile').annotate(
        complaint_count=Count('complaints')
    ).order_by('-date_joined')

    if search_query:
        citizens_qs = citizens_qs.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(profile__phone_number__icontains=search_query) |
            Q(profile__city__icontains=search_query)
        )

    paginator = Paginator(citizens_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_portal/citizen_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_citizens': citizens_qs.count()
    })
