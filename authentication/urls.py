from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),

    # Authentication endpoints
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Profile endpoints
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_public'),
    path('profile/update/', views.edit_profile_view, name='edit_profile'),

    # Sport preferences endpoints
    path('profile/sports/', views.sport_preferences_view, name='sport_preferences'),
    path('profile/sports/<int:sport_id>/', views.delete_sport_preference_view, name='delete_sport_preference'),
]
