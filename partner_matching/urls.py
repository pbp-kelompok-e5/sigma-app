from django.urls import path
from . import views

app_name = 'partner_matching'

urlpatterns = [
    path('browse/', views.browse_user, name='browse_user'),
    path('api/browse-users/', views.browse_user_ajax, name='browse_user_api'),
]