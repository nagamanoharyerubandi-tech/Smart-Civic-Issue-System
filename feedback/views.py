from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from accounts.decorators import citizen_required, admin_required
from complaints.models import Complaint
from .models import Feedback
from .forms import FeedbackForm
from notifications.utils import send_civic_notification
from django.contrib.auth.models import User


@login_required
@citizen_required
def citizen_submit_feedback(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, citizen=request.user)

    if complaint.status != 'Resolved':
        messages.warning(request, "Feedback can only be submitted once the complaint is officially marked Resolved.")
        return redirect('citizen_complaint_detail', complaint_id=complaint.id)

    # Check if feedback already exists
    feedback_instance = getattr(complaint, 'feedback', None)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback_instance)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.complaint = complaint
            fb.citizen = request.user
            fb.save()

            # Notify admin
            for admin in User.objects.filter(is_staff=True):
                send_civic_notification(
                    recipient=admin,
                    title=f"Citizen Feedback Received: {complaint.reference_id}",
                    message=f"{request.user.get_full_name() or request.user.username} rated {fb.rating} stars for complaint {complaint.reference_id}.",
                    notification_type='feedback_request',
                    complaint=complaint,
                    action_url='/admin-portal/feedback/'
                )

            messages.success(request, "Thank you! Your feedback has been submitted successfully.")
            return redirect('citizen_complaint_detail', complaint_id=complaint.id)
    else:
        form = FeedbackForm(instance=feedback_instance)

    return render(request, 'citizen/submit_feedback.html', {
        'form': form,
        'complaint': complaint,
        'existing_feedback': feedback_instance
    })


@login_required
@admin_required
def admin_feedback_list(request):
    rating_filter = request.GET.get('rating')
    feedback_qs = Feedback.objects.select_related('complaint', 'citizen', 'complaint__category', 'complaint__assigned_department').order_by('-created_at')

    if rating_filter and rating_filter.isdigit():
        feedback_qs = feedback_qs.filter(rating=int(rating_filter))

    paginator = Paginator(feedback_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Overall metrics
    total_feedbacks = Feedback.objects.count()
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

    # Rating distribution
    rating_counts = {}
    for r in range(1, 6):
        rating_counts[r] = Feedback.objects.filter(rating=r).count()

    context = {
        'page_obj': page_obj,
        'rating_filter': rating_filter,
        'total_feedbacks': total_feedbacks,
        'avg_rating': round(avg_rating, 1),
        'rating_counts': rating_counts,
    }
    return render(request, 'admin_portal/feedback_list.html', context)
