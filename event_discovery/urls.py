from django.urls import path
from . import views

app_name = 'event_discovery'

urlpatterns = [
    # Event discovery endpoints
    path('events/', views.show_event, name='show_event'),
    path('json/', views.show_json, name='show_json'),
    path('events/my-joined/', views.show_my_event, name='show_my_event'),
    
]