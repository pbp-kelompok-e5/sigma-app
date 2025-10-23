from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:event_id>/', views.event_reviews, name='event-reviews'),
    path('user/<int:user_id>/', views.user_reviews, name='user-reviews'),
    path('written/<int:user_id>/', views.user_written_reviews, name='user-written-reviews'),
    path('edit/<int:review_id>/', views.edit_review, name='edit-review'),

     # AJAX endpoints
    path('ajax/review/<int:review_id>/update/', views.ajax_update_review, name='ajax-update-review'),
    path('ajax/review/<int:review_id>/delete/', views.ajax_delete_review, name='ajax-delete-review'),
    path('ajax/event/<int:event_id>/create/', views.ajax_create_event_reviews, name='ajax-create-event-reviews'),
]