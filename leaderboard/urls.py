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
]