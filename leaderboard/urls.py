"""
URL Configuration untuk Leaderboard Module
Mendefinisikan routing untuk semua halaman leaderboard
"""

# Import fungsi path untuk routing
from django.urls import path
# Import views dari module ini
from . import views

# Namespace untuk URL leaderboard
# Digunakan untuk reverse URL: {% url 'leaderboard:leaderboard' %}
app_name = 'leaderboard'

urlpatterns = [
    # ===== LEADERBOARD =====
    # URL: /leaderboard/
    # View: leaderboard_page - Halaman leaderboard utama dengan ranking user
    path('', views.leaderboard_page, name='leaderboard'),

    # URL: /leaderboard/api/leaderboard/
    # View: leaderboard_api - AJAX API endpoint untuk data leaderboard (JSON)
    path('api/leaderboard/', views.leaderboard_api, name='leaderboard_api'),

    # ===== POINTS =====
    # URL: /leaderboard/points/dashboard/
    # View: points_dashboard - Dashboard poin user dengan breakdown aktivitas
    path('points/dashboard/', views.points_dashboard, name='points_dashboard'),

    # URL: /leaderboard/points/history/
    # View: points_history - History semua transaksi poin user
    path('points/history/', views.points_history, name='points_history'),

    # ===== ACHIEVEMENTS =====
    # URL: /leaderboard/achievements/
    # View: achievements_page - Halaman achievements user (earned + locked)
    path('achievements/', views.achievements_page, name='achievements'),

    # ===== FLUTTER MOBILE APP API ENDPOINTS =====
    # URL: /leaderboard/api/flutter/leaderboard/
    # View: flutter_leaderboard - JSON API endpoint untuk Flutter app (leaderboard data)
    path('api/flutter/leaderboard/', views.flutter_leaderboard, name='flutter_leaderboard'),

    # URL: /leaderboard/api/flutter/points/dashboard/
    # View: flutter_points_dashboard - JSON API endpoint untuk Flutter app (points dashboard)
    path('api/flutter/points/dashboard/', views.flutter_points_dashboard, name='flutter_points_dashboard'),

    # URL: /leaderboard/api/flutter/points/history/
    # View: flutter_points_history - JSON API endpoint untuk Flutter app (points history)
    path('api/flutter/points/history/', views.flutter_points_history, name='flutter_points_history'),
]