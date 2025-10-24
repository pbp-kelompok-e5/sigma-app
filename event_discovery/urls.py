from django.urls import path
from . import views

app_name = 'event_discovery'

urlpatterns = [
    # Event discovery endpoints
    path('events/', views.show_event, name='show_event'),
    path('events/json/', views.show_json, name='show_json'),
    path('events/my-joined/', views.show_my_event, name='show_my_event'),
    path('events/my-joined/json', views.show_json_my_event, name='show_json_my_event'),
    path('events/<uuid:id>/', views.event_detail, name='event_detail'),
    path('events/<uuid:id>/join', views.join_event, name='join_event'),
    path('events/<uuid:id>/leave', views.leave_event, name='leave_event'),
    path('events/<uuid:id>/json/', views.show_json_by_id, name='show_json_by_id'),
    path('events/<uuid:id>/participant-status/', views.event_participant_status, name='event_participant_status'),
]