from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'partner_matching'

def redirect_to_profile(request, user_id):
    """Redirect partner-matching profile to authentication profile"""
    from_param = request.GET.get('from', '')
    if from_param:
        return redirect(f'/profile/{user_id}/?from={from_param}')
    return redirect('authentication:profile_public', user_id=user_id)

urlpatterns = [
    path('browse/', views.browse_user, name='browse_user'),
    # path('api/browse-users/', views.browse_user_ajax, name='browse_user_api'),
    path('browse-users-api/', views.browse_user_ajax, name='browse_user_api'),

    # Redirect to authentication profile instead
    path('profile/<int:user_id>/', redirect_to_profile, name='user_profile'),
    path('connection/<str:action>/<int:user_id>/', views.connection_request, name='connection_request'),

    path('connections/', views.connections, name='connections'),
    path('profile/<int:user_id>/connections/', views.public_connections, name='public_connections'),

    path('connection/<str:action>/user/<int:user_id>/', views.connection_action_by_user, name='connection_action_by_user'),

    path('connections/api/', views.connections_api, name='connections_api'),
    path('profile/<int:user_id>/connections/api/', views.public_connections_api, name='public_connections_api'),

    path('filter-options-api/', views.get_filter_options_api, name='filter_options_api'),
    path('profile/<int:user_id>/api/', views.user_profile_detail_api, name='user_profile_detail_api'),
]