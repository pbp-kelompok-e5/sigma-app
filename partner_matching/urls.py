from django.urls import path
from . import views

app_name = 'partner_matching'

urlpatterns = [
    path('browse/', views.browse_user, name='browse_user'),
    # path('api/browse-users/', views.browse_user_ajax, name='browse_user_api'),
    path('browse-users-api/', views.browse_user_ajax, name='browse_user_api'),

    path('profile/<int:user_id>/', views.user_profile_detail, name='user_profile'),
    path('connection/<str:action>/<int:user_id>/', views.connection_request, name='connection_request'),
    path('icons-preview/', views.icon_preview, name='icon_preview'),

    path('connections/', views.connections, name='connections'),
    path('profile/<int:user_id>/connections/', views.public_connections, name='public_connections'),
    # path('connection/<str:action>/<int:connection_id>/', views.connection_action, name='connection_action'),
    path('connection/<str:action>/user/<int:user_id>/', views.connection_action_by_user, name='connection_action_by_user'),


]