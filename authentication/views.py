# Import fungsi-fungsi Django untuk routing dan HTTP response
from django.shortcuts import render, redirect, get_object_or_404
# Import fungsi autentikasi Django (login, logout, authenticate)
from django.contrib.auth import login, logout, authenticate
# Import decorator untuk membatasi akses hanya untuk user yang sudah login
from django.contrib.auth.decorators import login_required
# Import model User bawaan Django
from django.contrib.auth.models import User
# Import messages framework untuk menampilkan notifikasi ke user
from django.contrib import messages
# Import JsonResponse untuk mengembalikan response dalam format JSON (untuk AJAX)
from django.http import JsonResponse
# Import decorator untuk membatasi HTTP method yang diperbolehkan
from django.views.decorators.http import require_http_methods
# Import exception untuk validasi
from django.core.exceptions import ValidationError
# Import form-form custom dari aplikasi authentication
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, SportPreferenceForm
# Import model-model custom dari aplikasi authentication
from .models import UserProfile, SportPreference
# Import decorator untuk menonaktifkan CSRF protection (untuk Flutter mobile app)
from django.views.decorators.csrf import csrf_exempt
# Import JSON parser
import json


def home_redirect_view(request):
    """
    View untuk halaman home/landing page.
    - Jika user sudah login : redirect ke halaman profile
    - Jika user belum login : tampilkan landing page
    """
    if request.user.is_authenticated:
        # User sudah login, redirect ke profile
        return redirect('authentication:profile')
    else:
        # User belum login, tampilkan landing page
        return render(request, 'authentication/home.html')


def home_view(request):
    """
    View alternatif untuk home page.
    Kept for backward compatibility - memanggil home_redirect_view
    """
    return home_redirect_view(request)


def register_view(request):
    """
    View untuk registrasi user baru.
    Mendukung dua mode:
    1. Form submission biasa (redirect setelah sukses)
    2. AJAX request (return JSON response)
    """
    # Jika user sudah login, redirect ke profile (tidak perlu register lagi)
    if request.user.is_authenticated:
        return redirect('authentication:profile')

    if request.method == 'POST':
        # Cek apakah ini AJAX request dengan melihat header X-Requested-With
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Buat instance form dengan data dari POST request
        form = CustomUserCreationForm(request.POST)

        # Validasi form
        if form.is_valid():
            # Simpan user baru ke database
            form.save()
            # Ambil username dari cleaned_data untuk ditampilkan di pesan sukses
            username = form.cleaned_data.get('username')
            message = f'Account created for {username}! You can now log in.'

            # Jika AJAX request, return JSON response
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'redirect': '/auth/login/'
                })
            else:
                # Jika form submission biasa, tampilkan pesan sukses dan redirect
                messages.success(request, message, extra_tags='success')
                return redirect('authentication:login')
        else:
            # Form tidak valid, siapkan pesan error
            error_message = 'Please correct the errors below.'
            # Kumpulkan semua error dari setiap field
            errors = {field: form[field].errors for field in form.fields if form[field].errors}

            # Jika AJAX request, return JSON response dengan error
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message,
                    'errors': errors
                }, status=400)
            else:
                # Jika form submission biasa, tampilkan pesan error
                messages.error(request, error_message, extra_tags='error')
    else:
        # GET request, buat form kosong untuk ditampilkan
        form = CustomUserCreationForm()

    # Render template register dengan form
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """
    View untuk login user.
    Mendukung dua mode:
    1. Form submission biasa (redirect setelah sukses)
    2. AJAX request (return JSON response)
    """
    # Jika user sudah login, redirect ke profile (tidak perlu login lagi)
    if request.user.is_authenticated:
        return redirect('authentication:profile')

    if request.method == 'POST':
        # Cek apakah ini AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Buat instance form dengan request dan data POST
        # AuthenticationForm memerlukan request sebagai parameter pertama
        form = CustomAuthenticationForm(request, data=request.POST)

        # Validasi form
        if form.is_valid():
            # Ambil username dan password dari cleaned_data
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Autentikasi user dengan username dan password
            user = authenticate(username=username, password=password)

            # Jika autentikasi berhasil (user tidak None)
            if user is not None:
                # Login user (buat session)
                login(request, user)
                # Buat pesan welcome, gunakan first_name jika ada, jika tidak gunakan username
                message = f'Welcome back, {user.first_name or user.username}!'

                # Jika AJAX request, return JSON response
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': message,
                        'redirect': '/profile/'
                    })
                else:
                    # Jika form submission biasa, tampilkan pesan sukses dan redirect
                    messages.success(request, message, extra_tags='success')
                    # Cek apakah ada parameter 'next' di URL (untuk redirect setelah login)
                    next_url = request.GET.get('next', 'authentication:profile')
                    return redirect(next_url)

        # Form tidak valid atau autentikasi gagal
        error_message = 'Invalid username or password.'

        # Jika AJAX request, return JSON response dengan error
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': error_message
            }, status=401)
        else:
            # Jika form submission biasa, tampilkan pesan error
            messages.error(request, error_message, extra_tags='error')
    else:
        # GET request, buat form kosong untuk ditampilkan
        form = CustomAuthenticationForm()

    # Render template login dengan form
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """
    View untuk logout user.
    Menghapus session user dan redirect ke halaman login.
    """
    # Logout user (hapus session)
    logout(request)
    # Tampilkan pesan sukses
    messages.success(request, 'You have been logged out successfully.', extra_tags='success')
    # Redirect ke halaman login
    return redirect('authentication:login')


@login_required
def profile_view(request, user_id=None):
    """
    View untuk menampilkan profil user.
    Bisa menampilkan profil sendiri atau profil user lain (public profile).

    Args:
        user_id (int, optional): ID user yang profilnya akan ditampilkan.
                                 Jika None, tampilkan profil user yang sedang login.
    """
    if user_id:
        # Public profile view - melihat profil user lain
        # get_object_or_404 akan raise 404 jika user tidak ditemukan
        profile_user = get_object_or_404(User, id=user_id)
        # Cek apakah ini profil sendiri atau profil orang lain
        is_own_profile = request.user == profile_user
    else:
        # Private profile view - melihat profil sendiri
        profile_user = request.user
        is_own_profile = True

    try:
        # Ambil profile user (relasi one-to-one dengan User)
        profile = profile_user.profile
    except UserProfile.DoesNotExist:
        # Jika profile belum ada, buat profile baru
        # Ini adalah fallback jika signal tidak berjalan
        profile = UserProfile.objects.create(
            user=profile_user,
            full_name=profile_user.get_full_name() or profile_user.username
        )

    # Ambil semua preferensi olahraga user
    sport_preferences = profile_user.sport_preferences.all()

    # Import model Review dan fungsi agregasi Avg
    from reviews.models import Review
    from django.db.models import Avg

    # Ambil semua review yang ditulis oleh user ini
    # select_related untuk optimasi query (menghindari N+1 query problem)
    reviews_written = profile_user.reviews_given.all().select_related('to_user', 'event').order_by('-created_at')

    # Ambil semua review yang diterima oleh user ini
    reviews_received = profile_user.reviews_received.all().select_related('from_user', 'event').order_by('-created_at')

    # Hitung rata-rata rating yang diterima user
    # aggregate mengembalikan dict, ambil nilai 'rating__avg', jika None gunakan 0
    average_rating = reviews_received.aggregate(Avg('rating'))['rating__avg'] or 0

    # Cek status koneksi jika melihat profil user lain
    connection_status = None
    if not is_own_profile:
        # Import model Connection dan Q object untuk complex query
        from partner_matching.models import Connection
        from django.db.models import Q

        # Cek apakah sudah berteman (connection dengan status 'accepted')
        # Q object digunakan untuk OR condition (bisa from_user atau to_user)
        is_friends = Connection.objects.filter(
            Q(from_user=request.user, to_user=profile_user, status='accepted') |
            Q(from_user=profile_user, to_user=request.user, status='accepted')
        ).exists()

        if is_friends:
            # Sudah berteman
            connection_status = 'accepted'
        else:
            # Belum berteman, cek apakah ada pending request

            # Cek apakah current user sudah mengirim request ke profile_user
            sent_request = Connection.objects.filter(
                from_user=request.user,
                to_user=profile_user
            ).first()

            # Cek apakah profile_user sudah mengirim request ke current user
            received_request = Connection.objects.filter(
                from_user=profile_user,
                to_user=request.user
            ).first()

            if sent_request:
                # Ada request yang dikirim (pending)
                connection_status = 'pending'
            elif received_request:
                # Ada request yang diterima (pending)
                connection_status = 'pending'
            else:
                # Tidak ada koneksi sama sekali
                connection_status = None

    # Siapkan context untuk template
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'sport_preferences': sport_preferences,
        'is_own_profile': is_own_profile,
        'reviews_written': reviews_written,
        'reviews_received': reviews_received,
        'average_rating': average_rating,
        'connection_status': connection_status,
    }

    # Render template profile dengan context
    return render(request, 'authentication/profile.html', context)


@login_required
def edit_profile_view(request):
    """
    View untuk mengedit profil user.
    Mendukung dua mode:
    1. Form submission biasa (redirect setelah sukses)
    2. AJAX request (return JSON response dengan data profile yang diupdate)
    """
    try:
        # Ambil profile user yang sedang login
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Jika profile belum ada, buat profile baru
        # Ini adalah fallback jika signal tidak berjalan
        profile = UserProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username
        )

    if request.method == 'POST':
        # Cek apakah ini AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Buat instance form dengan data POST, instance profile yang akan diupdate, dan user
        form = UserProfileForm(request.POST, instance=profile, user=request.user)

        # Validasi form
        if form.is_valid():
            # Simpan perubahan profile
            form.save()
            message = 'Your profile has been updated successfully!'

            # Jika AJAX request, return JSON response dengan data profile yang diupdate
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'profile': {
                        'full_name': profile.full_name,
                        'email': request.user.email,
                        'city': profile.get_city_display(),  # get_city_display() untuk mendapatkan label dari choice
                    }
                })
            else:
                # Jika form submission biasa, tampilkan pesan sukses dan redirect
                messages.success(request, message, extra_tags='success')
                return redirect('authentication:profile')
        else:
            # Form tidak valid, siapkan pesan error
            error_message = 'Please correct the errors below.'
            # Kumpulkan semua error dari setiap field
            errors = {field: form[field].errors for field in form.fields if form[field].errors}

            # Jika AJAX request, return JSON response dengan error
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message,
                    'errors': errors
                }, status=400)
            else:
                # Jika form submission biasa, tampilkan pesan error
                messages.error(request, error_message, extra_tags='error')
    else:
        # GET request, buat form dengan instance profile yang ada
        form = UserProfileForm(instance=profile, user=request.user)

    # Render template edit profile dengan form
    return render(request, 'authentication/edit_profile.html', {'form': form})


@login_required
def sport_preferences_view(request):
    """
    View untuk melihat dan mengelola preferensi olahraga user.
    User bisa menambah preferensi olahraga baru di halaman ini.
    """
    # Ambil semua preferensi olahraga user yang sedang login
    sport_preferences = request.user.sport_preferences.all()

    if request.method == 'POST':
        # Buat instance form dengan data POST dan user
        form = SportPreferenceForm(request.POST, user=request.user)

        # Validasi form
        if form.is_valid():
            try:
                # Simpan preferensi olahraga baru
                form.save()
                # Tampilkan pesan sukses
                messages.success(request, 'Sport preference added successfully!', extra_tags='success')
                # Redirect ke halaman yang sama untuk refresh data
                return redirect('authentication:sport_preferences')
            except ValidationError as e:
                # Jika ada error validasi (misal duplikat sport_type), tampilkan pesan error
                messages.error(request, f'Error: {e.message}', extra_tags='error')
        else:
            # Form tidak valid, tampilkan pesan error
            messages.error(request, 'Please correct the errors below.', extra_tags='error')
    else:
        # GET request, buat form kosong untuk ditampilkan
        form = SportPreferenceForm(user=request.user)

    # Siapkan context untuk template
    context = {
        'sport_preferences': sport_preferences,
        'form': form,
    }

    # Render template sport preferences dengan context
    return render(request, 'authentication/sport_preferences.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_sport_preference_view(request, sport_id):
    """
    View untuk menghapus preferensi olahraga.
    Hanya menerima HTTP method DELETE.

    Args:
        sport_id (int): ID preferensi olahraga yang akan dihapus
    """
    try:
        # Ambil preferensi olahraga berdasarkan ID dan pastikan milik user yang sedang login
        # get_object_or_404 akan raise 404 jika tidak ditemukan
        preference = get_object_or_404(SportPreference, id=sport_id, user=request.user)

        # Ambil nama olahraga untuk ditampilkan di pesan sukses
        # get_sport_type_display() untuk mendapatkan label dari choice
        sport_name = preference.get_sport_type_display()

        # Hapus preferensi olahraga dari database
        preference.delete()

        # Cek apakah ini JSON request (AJAX)
        if request.headers.get('Content-Type') == 'application/json':
            # Return JSON response untuk AJAX request
            return JsonResponse({'success': True, 'message': f'{sport_name} preference removed successfully!'})
        else:
            # Tampilkan pesan sukses dan redirect untuk non-AJAX request
            messages.success(request, f'{sport_name} preference removed successfully!', extra_tags='success')
            return redirect('authentication:sport_preferences')
    except Exception:
        # Jika terjadi error, return response sesuai tipe request
        if request.headers.get('Content-Type') == 'application/json':
            # Return JSON response dengan error untuk AJAX request
            return JsonResponse({'success': False, 'message': 'Error removing sport preference.'})
        else:
            # Tampilkan pesan error untuk non-AJAX request
            messages.error(request, 'Error removing sport preference.', extra_tags='error')


# ===== FLUTTER MOBILE APP AUTHENTICATION ENDPOINTS =====
# These endpoints are specifically designed for Flutter mobile app integration
# They use @csrf_exempt decorator and accept/return JSON data


@csrf_exempt
@require_http_methods(["POST"])
def flutter_register(request):
    """
    Flutter-specific registration endpoint.

    Accepts JSON request body with:
    - username: string (required)
    - password1: string (required)
    - password2: string (required)

    Returns JSON response:
    {
        "status": true/false,
        "message": "Success or error message",
        "username": "created_username" (only on success)
    }

    HTTP Status Codes:
    - 200: Registration successful
    - 400: Validation errors (passwords don't match, username exists, etc.)
    """
    try:
        # Parse JSON request body
        data = json.loads(request.body)

        # Extract required fields
        username = data.get('username', '').strip()
        password1 = data.get('password1', '')
        password2 = data.get('password2', '')

        # Validate required fields
        if not username or not password1 or not password2:
            return JsonResponse({
                'status': False,
                'message': 'Username and passwords are required.'
            }, status=400)

        # Check if passwords match
        if password1 != password2:
            return JsonResponse({
                'status': False,
                'message': 'Passwords do not match.'
            }, status=400)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': False,
                'message': 'Username already exists.'
            }, status=400)

        # Validate password strength using Django's built-in validators
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password1, user=None)
        except ValidationError as e:
            return JsonResponse({
                'status': False,
                'message': ' '.join(e.messages)
            }, status=400)

        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password1
        )

        # UserProfile will be auto-created by signal in models.py

        return JsonResponse({
            'status': True,
            'message': 'User created successfully!',
            'username': username
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': False,
            'message': 'Invalid JSON format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def flutter_login(request):
    """
    Flutter-specific login endpoint.

    Accepts JSON request body with:
    - username: string (required)
    - password: string (required)

    Returns JSON response:
    {
        "status": true/false,
        "message": "Success or error message",
        "username": "authenticated_username" (only on success)
    }

    HTTP Status Codes:
    - 200: Login successful
    - 401: Authentication failed (invalid credentials)
    """
    try:
        # Parse JSON request body
        data = json.loads(request.body)

        # Extract credentials
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # Validate required fields
        if not username or not password:
            return JsonResponse({
                'status': False,
                'message': 'Username and password are required.'
            }, status=401)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login successful - create session
            login(request, user)

            return JsonResponse({
                'status': True,
                'message': 'Login successful!',
                'username': username
            }, status=200)
        else:
            # Authentication failed
            return JsonResponse({
                'status': False,
                'message': 'Invalid username or password.'
            }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': False,
            'message': 'Invalid JSON format.'
        }, status=401)
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def flutter_logout(request):
    """
    Flutter-specific logout endpoint.

    Invalidates the user's session.

    Returns JSON response:
    {
        "status": true,
        "message": "Logout successful!"
    }

    HTTP Status Codes:
    - 200: Logout successful
    """
    try:
        # Logout user (invalidate session)
        logout(request)

        return JsonResponse({
            'status': True,
            'message': 'Logout successful!'
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=200)  # Still return 200 even on error for logout


@csrf_exempt
@require_http_methods(["GET"])
def flutter_profile(request, user_id=None):
    """
    Flutter-specific profile endpoint.

    GET /auth/flutter/profile/ - Returns authenticated user's own profile
    GET /auth/flutter/profile/<user_id>/ - Returns another user's profile by ID

    Returns JSON response:
    {
        "status": true/false,
        "message": "Success or error message",
        "data": {
            "user": {
                "id": int,
                "username": "string",
                "email": "string",
                "first_name": "string",
                "last_name": "string"
            },
            "profile": {
                "full_name": "string",
                "bio": "string",
                "city": "string",
                "city_display": "string",
                "profile_image_url": "string",
                "total_points": int,
                "total_events": int,
                "created_at": "ISO datetime string"
            },
            "sport_preferences": [
                {
                    "id": int,
                    "sport_type": "string",
                    "sport_type_display": "string",
                    "skill_level": "string",
                    "skill_level_display": "string",
                    "created_at": "ISO datetime string"
                }
            ],
            "is_own_profile": true/false
        }
    }

    HTTP Status Codes:
    - 200: Success
    - 401: Not authenticated
    - 404: User not found
    """
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': False,
                'message': 'Authentication required.'
            }, status=401)

        # Determine which user's profile to fetch
        if user_id:
            # Fetch another user's profile
            try:
                profile_user = User.objects.get(id=user_id)
                is_own_profile = request.user == profile_user
            except User.DoesNotExist:
                return JsonResponse({
                    'status': False,
                    'message': 'User not found.'
                }, status=404)
        else:
            # Fetch authenticated user's own profile
            profile_user = request.user
            is_own_profile = True

        # Get or create user profile
        try:
            profile = profile_user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist (fallback)
            profile = UserProfile.objects.create(
                user=profile_user,
                full_name=profile_user.get_full_name() or profile_user.username
            )

        # Get sport preferences
        sport_preferences = profile_user.sport_preferences.all()

        # Serialize sport preferences
        sport_prefs_data = [
            {
                'id': pref.id,
                'sport_type': pref.sport_type,
                'sport_type_display': pref.get_sport_type_display(),
                'skill_level': pref.skill_level,
                'skill_level_display': pref.get_skill_level_display(),
                'created_at': pref.created_at.isoformat()
            }
            for pref in sport_preferences
        ]

        # Build response data
        response_data = {
            'user': {
                'id': profile_user.id,
                'username': profile_user.username,
                'email': profile_user.email,
                'first_name': profile_user.first_name,
                'last_name': profile_user.last_name
            },
            'profile': {
                'full_name': profile.full_name,
                'bio': profile.bio or '',
                'city': profile.city,
                'city_display': profile.get_city_display() if profile.city else '',
                'profile_image_url': profile.profile_image_url or '',
                'total_points': profile.total_points,
                'total_events': profile.total_events,
                'created_at': profile.created_at.isoformat()
            },
            'sport_preferences': sport_prefs_data,
            'is_own_profile': is_own_profile
        }

        return JsonResponse({
            'status': True,
            'message': 'Profile fetched successfully!',
            'data': response_data
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# ===== FLUTTER PROFILE UPDATE ENDPOINT =====
@csrf_exempt
@require_http_methods(["POST", "PUT", "PATCH"])
def flutter_profile_update(request):
    """
    Update authenticated user's profile information.

    Endpoint: POST/PUT/PATCH /auth/flutter/profile/update/

    Request Body (JSON):
    {
        "full_name": "string",
        "bio": "string",
        "city": "string"  // Must be from CITY_CHOICES
    }

    Response (200):
    {
        "status": true,
        "message": "Profile updated successfully",
        "data": {
            "full_name": "string",
            "bio": "string",
            "city": "string",
            "city_display": "string"
        }
    }

    Response (401):
    {
        "status": false,
        "message": "Authentication required"
    }

    Response (400):
    {
        "status": false,
        "message": "Validation error message"
    }
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Authentication required'
        }, status=401)

    try:
        # Parse JSON request body
        data = json.loads(request.body)

        # Get user's profile
        profile = request.user.profile

        # Update fields if provided
        if 'full_name' in data:
            full_name = data['full_name'].strip()
            if not full_name:
                return JsonResponse({
                    'status': False,
                    'message': 'Full name cannot be empty'
                }, status=400)
            profile.full_name = full_name

        if 'bio' in data:
            profile.bio = data['bio'].strip()

        if 'city' in data:
            city = data['city']
            # Validate city is in CITY_CHOICES
            valid_cities = [choice[0] for choice in profile._meta.get_field('city').choices]
            if city not in valid_cities:
                return JsonResponse({
                    'status': False,
                    'message': f'Invalid city: {city}'
                }, status=400)
            profile.city = city

        # Save the profile
        profile.save()

        # Return updated profile data
        return JsonResponse({
            'status': True,
            'message': 'Profile updated successfully',
            'data': {
                'full_name': profile.full_name,
                'bio': profile.bio or '',
                'city': profile.city,
                'city_display': profile.get_city_display()
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': False,
            'message': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# ===== FLUTTER SPORT PREFERENCE ADD ENDPOINT =====
@csrf_exempt
@require_http_methods(["POST"])
def flutter_sport_preference_add(request):
    """
    Add a new sport preference for the authenticated user.

    Endpoint: POST /auth/flutter/profile/sport-preferences/add/

    Request Body (JSON):
    {
        "sport_type": "string",  // Must be from SPORT_CHOICES
        "skill_level": "string"  // Must be from SKILL_CHOICES
    }

    Response (200):
    {
        "status": true,
        "message": "Sport preference added successfully",
        "data": {
            "id": 1,
            "sport_type": "string",
            "sport_type_display": "string",
            "skill_level": "string",
            "skill_level_display": "string",
            "created_at": "2024-01-01T10:00:00Z"
        }
    }

    Response (400):
    {
        "status": false,
        "message": "Error message"
    }
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Authentication required'
        }, status=401)

    try:
        # Parse JSON request body
        data = json.loads(request.body)

        # Validate required fields
        sport_type = data.get('sport_type')
        skill_level = data.get('skill_level')

        if not sport_type or not skill_level:
            return JsonResponse({
                'status': False,
                'message': 'sport_type and skill_level are required'
            }, status=400)

        # Check if user already has this sport preference
        existing = SportPreference.objects.filter(
            user=request.user,
            sport_type=sport_type
        ).first()

        if existing:
            return JsonResponse({
                'status': False,
                'message': f'You already have a preference for {existing.get_sport_type_display()}'
            }, status=400)

        # Create new sport preference
        sport_pref = SportPreference.objects.create(
            user=request.user,
            sport_type=sport_type,
            skill_level=skill_level
        )

        # Return created sport preference
        return JsonResponse({
            'status': True,
            'message': 'Sport preference added successfully',
            'data': {
                'id': sport_pref.id,
                'sport_type': sport_pref.sport_type,
                'sport_type_display': sport_pref.get_sport_type_display(),
                'skill_level': sport_pref.skill_level,
                'skill_level_display': sport_pref.get_skill_level_display(),
                'created_at': sport_pref.created_at.isoformat()
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': False,
            'message': 'Invalid JSON format'
        }, status=400)

    except ValidationError as e:
        return JsonResponse({
            'status': False,
            'message': str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# ===== FLUTTER SPORT PREFERENCE DELETE ENDPOINT =====
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def flutter_sport_preference_delete(request, preference_id):
    """
    Delete a sport preference for the authenticated user.

    Endpoint: DELETE /auth/flutter/profile/sport-preferences/<preference_id>/delete/

    Response (200):
    {
        "status": true,
        "message": "Sport preference deleted successfully"
    }

    Response (404):
    {
        "status": false,
        "message": "Sport preference not found"
    }
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Authentication required'
        }, status=401)

    try:
        # Get sport preference
        sport_pref = SportPreference.objects.get(
            id=preference_id,
            user=request.user
        )

        # Delete the sport preference
        sport_pref.delete()

        return JsonResponse({
            'status': True,
            'message': 'Sport preference deleted successfully'
        }, status=200)

    except SportPreference.DoesNotExist:
        return JsonResponse({
            'status': False,
            'message': 'Sport preference not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# ===== FLUTTER PROFILE IMAGE UPLOAD ENDPOINT =====
@csrf_exempt
@require_http_methods(["POST"])
def flutter_profile_image_upload(request):
    """
    Upload profile image URL for the authenticated user.

    Note: This endpoint accepts a URL string, not a file upload.
    For actual file uploads, you would need to configure media storage.

    Endpoint: POST /auth/flutter/profile/upload-image/

    Request Body (JSON):
    {
        "profile_image_url": "string"  // URL to the profile image
    }

    Response (200):
    {
        "status": true,
        "message": "Profile image updated successfully",
        "data": {
            "profile_image_url": "string"
        }
    }

    Response (400):
    {
        "status": false,
        "message": "Error message"
    }
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': False,
            'message': 'Authentication required'
        }, status=401)

    try:
        # Parse JSON request body
        data = json.loads(request.body)

        # Get profile image URL
        profile_image_url = data.get('profile_image_url', '').strip()

        if not profile_image_url:
            return JsonResponse({
                'status': False,
                'message': 'profile_image_url is required'
            }, status=400)

        # Basic URL validation
        if not (profile_image_url.startswith('http://') or profile_image_url.startswith('https://')):
            return JsonResponse({
                'status': False,
                'message': 'Invalid URL format. Must start with http:// or https://'
            }, status=400)

        # Update user's profile
        profile = request.user.profile
        profile.profile_image_url = profile_image_url
        profile.save()

        return JsonResponse({
            'status': True,
            'message': 'Profile image updated successfully',
            'data': {
                'profile_image_url': profile.profile_image_url
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': False,
            'message': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)