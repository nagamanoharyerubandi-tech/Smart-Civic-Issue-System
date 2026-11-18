from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CitizenRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .models import Profile
from notifications.utils import send_civic_notification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Profile is auto-created by signal, update extra fields
            profile = user.profile
            profile.role = 'citizen'
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.city = form.cleaned_data.get('city', 'Metropolis City')
            profile.address = form.cleaned_data.get('address', '')
            profile.save()

            # Welcome notification
            send_civic_notification(
                recipient=user,
                title="Welcome to Smart Civic Portal",
                message="Your citizen account has been successfully created. You can now report community issues, upload photos, and track progress.",
                notification_type='general',
                action_url='/citizen/complaints/create/'
            )

            messages.success(request, "Registration successful! You can now log in to your account.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = CitizenRegistrationForm()

    return render(request, 'public/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Support login with either username or email
            user = None
            if '@' in username_or_email:
                try:
                    u_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(request, username=u_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect('dashboard_redirect')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'public/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('home')


@login_required
def dashboard_redirect(request):
    profile = getattr(request.user, 'profile', None)
    if request.user.is_staff or request.user.is_superuser or (profile and profile.is_administrator):
        return redirect('admin_dashboard')
    return redirect('citizen_dashboard')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors in the profile form.")
    else:
        form = UserProfileUpdateForm(instance=profile, user=request.user)

    template = 'admin_portal/profile.html' if profile.is_administrator else 'citizen/profile.html'
    return render(request, template, {'form': form, 'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully changed!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    is_admin = getattr(request.user, 'profile', None) and request.user.profile.is_administrator
    template = 'admin_portal/change_password.html' if is_admin else 'citizen/change_password.html'
    return render(request, template, {'form': form})
