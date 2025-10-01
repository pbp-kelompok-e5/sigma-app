from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, SportPreferenceForm
from .models import UserProfile, SportPreference


def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Show dashboard for authenticated users
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.username
            )

        sport_preferences = request.user.sport_preferences.all()

        context = {
            'profile': profile,
            'sport_preferences': sport_preferences,
        }
        return render(request, 'authentication/dashboard.html', context)
    else:
        # Show landing page for anonymous users
        return render(request, 'authentication/home.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('authentication:profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('authentication:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('authentication:profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'authentication:profile')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('authentication:login')


@login_required
def profile_view(request, user_id=None):
    """View user profile (public or private)"""
    if user_id:
        # Public profile view
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = request.user == profile_user
    else:
        # Private profile view (own profile)
        profile_user = request.user
        is_own_profile = True

    try:
        profile = profile_user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=profile_user,
            full_name=profile_user.get_full_name() or profile_user.username
        )

    sport_preferences = profile_user.sport_preferences.all()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'sport_preferences': sport_preferences,
        'is_own_profile': is_own_profile,
    }

    return render(request, 'authentication/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username
        )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('authentication:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'authentication/edit_profile.html', {'form': form})


@login_required
def sport_preferences_view(request):
    """View and manage sport preferences"""
    sport_preferences = request.user.sport_preferences.all()

    if request.method == 'POST':
        form = SportPreferenceForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Sport preference added successfully!')
                return redirect('authentication:sport_preferences')
            except ValidationError as e:
                messages.error(request, f'Error: {e.message}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SportPreferenceForm(user=request.user)

    context = {
        'sport_preferences': sport_preferences,
        'form': form,
    }

    return render(request, 'authentication/sport_preferences.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_sport_preference_view(request, sport_id):
    """Delete a sport preference"""
    try:
        preference = get_object_or_404(SportPreference, id=sport_id, user=request.user)
        sport_name = preference.get_sport_type_display()
        preference.delete()

        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True, 'message': f'{sport_name} preference removed successfully!'})
        else:
            messages.success(request, f'{sport_name} preference removed successfully!')
            return redirect('authentication:sport_preferences')
    except Exception:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Error removing sport preference.'})
        else:
            messages.error(request, 'Error removing sport preference.')
            return redirect('authentication:sport_preferences')