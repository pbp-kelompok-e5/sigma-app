# Import fungsi path untuk mendefinisikan URL pattern
from django.urls import path
# Import views dari aplikasi authentication
from . import views

# Namespace untuk URL pattern aplikasi authentication
# Digunakan untuk reverse URL dengan format 'authentication:nama_url'
app_name = 'authentication'

# Daftar URL pattern untuk aplikasi authentication
urlpatterns = [
    # ===== HOME PAGE =====
    # URL: /
    # View: home_redirect_view
    # Redirect ke profile jika sudah login, tampilkan landing page jika belum
    path('', views.home_redirect_view, name='home'),

    # ===== AUTHENTICATION ENDPOINTS =====
    # URL: /auth/register/
    # View: register_view
    # Halaman registrasi user baru
    path('auth/register/', views.register_view, name='register'),

    # URL: /auth/login/
    # View: login_view
    # Halaman login user
    path('auth/login/', views.login_view, name='login'),

    # URL: /auth/logout/
    # View: logout_view
    # Endpoint untuk logout user (tidak ada halaman, langsung redirect)
    path('auth/logout/', views.logout_view, name='logout'),

    # ===== PROFILE ENDPOINTS =====
    # URL: /profile/
    # View: profile_view (tanpa user_id parameter)
    # Halaman profil user yang sedang login (private profile)
    path('profile/', views.profile_view, name='profile'),

    # URL: /profile/<user_id>/
    # View: profile_view (dengan user_id parameter)
    # Halaman profil user lain (public profile)
    path('profile/<int:user_id>/', views.profile_view, name='profile_public'),

    # URL: /profile/update/
    # View: edit_profile_view
    # Halaman untuk mengedit profil user yang sedang login
    path('profile/update/', views.edit_profile_view, name='edit_profile'),

    # ===== SPORT PREFERENCES ENDPOINTS =====
    # URL: /profile/sports/
    # View: sport_preferences_view
    # Halaman untuk melihat dan menambah preferensi olahraga
    path('profile/sports/', views.sport_preferences_view, name='sport_preferences'),

    # URL: /profile/sports/<sport_id>/
    # View: delete_sport_preference_view
    # Endpoint untuk menghapus preferensi olahraga (DELETE method only)
    path('profile/sports/<int:sport_id>/', views.delete_sport_preference_view, name='delete_sport_preference'),

    # ===== FLUTTER MOBILE APP AUTHENTICATION ENDPOINTS =====
    # URL: /auth/flutter/register/
    # View: flutter_register
    # JSON API endpoint untuk registrasi user dari Flutter mobile app
    path('auth/flutter/register/', views.flutter_register, name='flutter_register'),

    # URL: /auth/flutter/login/
    # View: flutter_login
    # JSON API endpoint untuk login user dari Flutter mobile app
    path('auth/flutter/login/', views.flutter_login, name='flutter_login'),

    # URL: /auth/flutter/logout/
    # View: flutter_logout
    # JSON API endpoint untuk logout user dari Flutter mobile app
    path('auth/flutter/logout/', views.flutter_logout, name='flutter_logout'),

    # ===== FLUTTER MOBILE APP PROFILE ENDPOINTS =====
    # URL: /auth/flutter/profile/
    # View: flutter_profile (tanpa user_id parameter)
    # JSON API endpoint untuk mendapatkan profil user yang sedang login
    path('auth/flutter/profile/', views.flutter_profile, name='flutter_profile'),

    # URL: /auth/flutter/profile/<user_id>/
    # View: flutter_profile (dengan user_id parameter)
    # JSON API endpoint untuk mendapatkan profil user lain berdasarkan ID
    path('auth/flutter/profile/<int:user_id>/', views.flutter_profile, name='flutter_profile_public'),

    # ===== FLUTTER MOBILE APP PROFILE MANAGEMENT ENDPOINTS =====
    # URL: /auth/flutter/profile/update/
    # View: flutter_profile_update
    # JSON API endpoint untuk update profil user yang sedang login
    path('auth/flutter/profile/update/', views.flutter_profile_update, name='flutter_profile_update'),

    # URL: /auth/flutter/profile/upload-image/
    # View: flutter_profile_image_upload
    # JSON API endpoint untuk upload URL gambar profil
    path('auth/flutter/profile/upload-image/', views.flutter_profile_image_upload, name='flutter_profile_image_upload'),

    # URL: /auth/flutter/profile/sport-preferences/add/
    # View: flutter_sport_preference_add
    # JSON API endpoint untuk menambah preferensi olahraga
    path('auth/flutter/profile/sport-preferences/add/', views.flutter_sport_preference_add, name='flutter_sport_preference_add'),

    # URL: /auth/flutter/profile/sport-preferences/<preference_id>/delete/
    # View: flutter_sport_preference_delete
    # JSON API endpoint untuk menghapus preferensi olahraga
    path('auth/flutter/profile/sport-preferences/<int:preference_id>/delete/', views.flutter_sport_preference_delete, name='flutter_sport_preference_delete'),
]
