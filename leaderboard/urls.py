from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    # Leaderboard
    path('', views.leaderboard_page, name='leaderboard'),

    # Points
    path('points/dashboard/', views.points_dashboard, name='points_dashboard'),
    path('points/history/', views.points_history, name='points_history'),

    # Achievements
    path('achievements/', views.achievements_page, name='achievements'),
]