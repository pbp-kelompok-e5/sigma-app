# event_management/urls.py
from django.urls import path
from . import views
from . import api   # new

app_name = 'event_management'

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('<int:event_id>/edit/', views.update_event, name='update_event'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('<int:event_id>/cancel/', views.cancel_event, name='cancel_event'),
    path('<int:event_id>/participants/', views.manage_participants, name='manage_participants'),

    # API routes (JSON) for mobile app
    path('api/my-events/', api.api_my_events, name='api_my_events'),
    path('api/events/<int:event_id>/', api.api_event_detail, name='api_event_detail'),
    path('api/events/create/', api.api_create_event, name='api_create_event'),
    path('api/events/<int:event_id>/update/', api.api_update_event, name='api_update_event'),
    path('api/events/<int:event_id>/delete/', api.api_delete_event, name='api_delete_event'),
    path('api/events/<int:event_id>/participants/', api.api_participants_list, name='api_participants_list'),
    path('api/events/<int:event_id>/participants/manage/', api.api_manage_participant, name='api_manage_participant'),
]
