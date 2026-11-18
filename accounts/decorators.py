from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def citizen_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a citizen.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if profile and profile.is_administrator and not profile.is_citizen:
            messages.info(request, "Redirected to Administrator Dashboard.")
            return redirect('admin_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has administrator role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Administrator login required.")
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        is_admin = (
            request.user.is_staff or
            request.user.is_superuser or
            (profile and profile.is_administrator)
        )
        if not is_admin:
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('citizen_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
