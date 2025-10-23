from django.urls import path
from . import views

app_name = 'event_management'

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('<int:event_id>/edit/', views.update_event, name='update_event'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('<int:event_id>/cancel/', views.cancel_event, name='cancel_event'),
    path('<int:event_id>/participants/', views.manage_participants, name='manage_participants'),
    # AJAX endpoints
    path('<int:event_id>/delete-ajax/', views.delete_event_ajax, name='delete_event_ajax'),
    path('<int:event_id>/cancel-ajax/', views.cancel_event_ajax, name='cancel_event_ajax'),
    path('<int:event_id>/participants-ajax/', views.manage_participant_ajax, name='manage_participant_ajax'),
    path('create-ajax/', views.create_event_ajax, name='create_event_ajax'),
    path('<int:event_id>/update-ajax/', views.update_event_ajax, name='update_event_ajax'),
]
