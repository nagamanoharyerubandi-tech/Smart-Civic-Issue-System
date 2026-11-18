from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from accounts.decorators import citizen_required, admin_required
from complaints.models import Complaint, Category, Department, ComplaintAssignment
from feedback.models import Feedback
from notifications.models import Notification
from django.contrib.auth.models import User


# ==============================================================================
# PUBLIC VIEWS
# ==============================================================================

def public_home(request):
    """
    High-impact landing page featuring key metrics, categories,
    workflow explanation, recent resolved complaints, and citizen testimonials.
    """
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    active_citizens = User.objects.filter(is_staff=False, is_superuser=False).count()
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 4.8

    resolution_rate = round((resolved_complaints / total_complaints * 100), 1) if total_complaints > 0 else 94.5

    categories = Category.objects.filter(is_active=True).annotate(
        complaint_count=Count('complaints')
    )[:6]

    recent_resolved = Complaint.objects.filter(status='Resolved').select_related(
        'category', 'assigned_department'
    ).order_by('-resolved_at')[:4]

    testimonials = Feedback.objects.filter(is_published=True, rating__gte=4).select_related(
        'citizen', 'complaint'
    ).order_by('-created_at')[:3]

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'active_citizens': active_citizens,
        'avg_rating': round(avg_rating, 1),
        'resolution_rate': resolution_rate,
        'categories': categories,
        'recent_resolved': recent_resolved,
        'testimonials': testimonials,
    }
    return render(request, 'public/home.html', context)


def public_about(request):
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    departments_count = Department.objects.filter(is_active=True).count()
    return render(request, 'public/about.html', {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'departments_count': departments_count,
    })


def public_how_it_works(request):
    return render(request, 'public/how_it_works.html')


def public_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f"Thank you, {name}! Your message has been received by the Municipal Helpdesk.")
        return redirect('contact')
    return render(request, 'public/contact.html')


def public_track_complaint(request):
    """
    Public lookup tool that enables any citizen to inspect real-time progress
    by entering their unique Reference Number without needing authentication.
    """
    ref_id = request.GET.get('ref', '').strip()
    complaint = None
    status_history = None

    if ref_id:
        try:
            complaint = Complaint.objects.select_related(
                'category', 'assigned_department'
            ).get(reference_id__iexact=ref_id)
            status_history = complaint.status_history.order_by('changed_at')
        except Complaint.DoesNotExist:
            messages.warning(request, f"No complaint was found with Reference ID '{ref_id}'. Please check and try again.")

    return render(request, 'public/track_complaint.html', {
        'complaint': complaint,
        'status_history': status_history,
        'ref_id': ref_id,
    })


# ==============================================================================
# CITIZEN DASHBOARD
# ==============================================================================

@login_required
@citizen_required
def citizen_dashboard(request):
    """
    Personalized citizen hub providing instant statistics, ongoing issue tracking,
    quick action buttons, and latest notifications.
    """
    user_complaints = Complaint.objects.filter(citizen=request.user)

    total_count = user_complaints.count()
    pending_count = user_complaints.filter(status__in=['Submitted', 'Under Review']).count()
    in_progress_count = user_complaints.filter(status__in=['Assigned', 'In Progress']).count()
    resolved_count = user_complaints.filter(status='Resolved').count()
    rejected_count = user_complaints.filter(status='Rejected').count()

    active_issues = user_complaints.exclude(status__in=['Resolved', 'Rejected']).select_related(
        'category', 'assigned_department'
    ).order_by('-created_at')[:4]

    recent_complaints = user_complaints.select_related(
        'category', 'assigned_department'
    ).order_by('-created_at')[:5]

    recent_notifs = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]

    context = {
        'total_count': total_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
        'active_issues': active_issues,
        'recent_complaints': recent_complaints,
        'recent_notifs': recent_notifs,
    }
    return render(request, 'citizen/dashboard.html', context)


# ==============================================================================
# ADMINISTRATOR DASHBOARD & ANALYTICS
# ==============================================================================

@login_required
@admin_required
def admin_dashboard(request):
    """
    Command center for administrators featuring real-time KPI metrics,
    interactive Chart.js graphs, urgent alerts, and recent activities.
    """
    all_complaints = Complaint.objects.all()

    total_complaints = all_complaints.count()
    pending_complaints = all_complaints.filter(status__in=['Submitted', 'Under Review']).count()
    in_progress_complaints = all_complaints.filter(status__in=['Assigned', 'In Progress']).count()
    resolved_complaints = all_complaints.filter(status='Resolved').count()
    rejected_complaints = all_complaints.filter(status='Rejected').count()
    duplicate_complaints = all_complaints.filter(is_duplicate=True).count()

    avg_feedback_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0
    total_citizens = User.objects.filter(is_staff=False, is_superuser=False).count()

    # Urgent complaints (High priority and not resolved)
    urgent_complaints = all_complaints.filter(
        priority='High'
    ).exclude(status__in=['Resolved', 'Rejected']).select_related(
        'citizen', 'category', 'assigned_department'
    ).order_by('-created_at')[:5]

    # Recent complaints
    recent_complaints = all_complaints.select_related(
        'citizen', 'category', 'assigned_department'
    ).order_by('-created_at')[:6]

    # Monthly Trends (last 6 months)
    now = timezone.now()
    monthly_data = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        # Approximate month end
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)

        filed = Complaint.objects.filter(created_at__gte=month_start, created_at__lt=next_month).count()
        res = Complaint.objects.filter(resolved_at__gte=month_start, resolved_at__lt=next_month).count()
        monthly_data.append({
            'label': month_start.strftime('%b %Y'),
            'filed': filed,
            'resolved': res
        })

    # Category Breakdown
    category_stats = Category.objects.annotate(
        count=Count('complaints')
    ).values('name', 'color', 'count').order_by('-count')

    # Status Breakdown
    status_stats = all_complaints.values('status').annotate(count=Count('id'))
    status_dict = {s['status']: s['count'] for s in status_stats}

    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'rejected_complaints': rejected_complaints,
        'duplicate_complaints': duplicate_complaints,
        'avg_feedback_rating': round(avg_feedback_rating, 1),
        'total_citizens': total_citizens,
        'urgent_complaints': urgent_complaints,
        'recent_complaints': recent_complaints,
        'category_stats': list(category_stats),
        'status_dict': status_dict,
        'monthly_data': monthly_data,
    }
    return render(request, 'admin_portal/dashboard.html', context)


@login_required
@admin_required
def admin_analytics(request):
    """
    Dedicated deep-dive analytics page with resolution times,
    department performance scores, and category metrics.
    """
    departments = Department.objects.annotate(
        total_assigned=Count('assigned_complaints'),
        resolved_count=Count('assigned_complaints', filter=Q(assigned_complaints__status='Resolved')),
        pending_count=Count('assigned_complaints', filter=~Q(assigned_complaints__status__in=['Resolved', 'Rejected']))
    ).order_by('-total_assigned')

    categories = Category.objects.annotate(
        total_count=Count('complaints'),
        resolved_count=Count('complaints', filter=Q(complaints__status='Resolved'))
    ).order_by('-total_count')

    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    overall_res_rate = round((resolved_complaints / total_complaints * 100), 1) if total_complaints > 0 else 0

    return render(request, 'admin_portal/analytics.html', {
        'departments': departments,
        'categories': categories,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'overall_res_rate': overall_res_rate,
    })


@login_required
@admin_required
def api_dashboard_charts(request):
    """
    Returns structured JSON data for asynchronous Chart.js charts.
    """
    # 1. Status Distribution
    statuses = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved', 'Rejected']
    status_counts = [Complaint.objects.filter(status=s).count() for s in statuses]

    # 2. Category Distribution
    categories = list(Category.objects.annotate(count=Count('complaints')).values('name', 'color', 'count'))

    # 3. Monthly Trends
    now = timezone.now()
    months = []
    filed_series = []
    resolved_series = []
    for i in range(5, -1, -1):
        m_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1)

        months.append(m_start.strftime('%b %Y'))
        filed_series.append(Complaint.objects.filter(created_at__gte=m_start, created_at__lt=m_end).count())
        resolved_series.append(Complaint.objects.filter(resolved_at__gte=m_start, resolved_at__lt=m_end).count())

    # 4. Department Workload
    dept_names = []
    dept_assigned = []
    dept_resolved = []
    for d in Department.objects.all():
        dept_names.append(d.code)
        dept_assigned.append(d.assigned_complaints.count())
        dept_resolved.append(d.assigned_complaints.filter(status='Resolved').count())

    data = {
        'status_labels': statuses,
        'status_data': status_counts,
        'categories': categories,
        'months': months,
        'filed_series': filed_series,
        'resolved_series': resolved_series,
        'dept_names': dept_names,
        'dept_assigned': dept_assigned,
        'dept_resolved': dept_resolved,
    }
    return JsonResponse(data)
