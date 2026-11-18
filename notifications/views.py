from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    filter_type = request.GET.get('filter', 'all')
    notifs_qs = Notification.objects.filter(recipient=request.user).select_related('complaint')

    if filter_type == 'unread':
        notifs_qs = notifs_qs.filter(is_read=False)

    paginator = Paginator(notifs_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    is_admin = getattr(request.user, 'profile', None) and request.user.profile.is_administrator
    template = 'admin_portal/notification_list.html' if is_admin else 'citizen/notification_list.html'

    return render(request, template, {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'unread_count': unread_count,
    })


@login_required
def notification_mark_read(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()

    if notif.action_url:
        return redirect(notif.action_url)

    is_admin = getattr(request.user, 'profile', None) and request.user.profile.is_administrator
    return redirect('admin_notifications' if is_admin else 'citizen_notifications')


@login_required
def notification_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    is_admin = getattr(request.user, 'profile', None) and request.user.profile.is_administrator
    return redirect('admin_notifications' if is_admin else 'citizen_notifications')
