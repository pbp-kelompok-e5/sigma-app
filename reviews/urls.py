from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:event_id>/', views.event_reviews, name='event-reviews'),
    path('user/<int:user_id>/', views.user_reviews, name='user-reviews'),
    path('written/<int:user_id>/', views.user_written_reviews, name='user-written-reviews'),
    path('edit/<int:review_id>/', views.edit_review, name='edit-review'),

     # AJAX endpoints
    path('ajax/update/<int:review_id>/', views.ajax_update_review, name='ajax_update_review'),
    path('ajax/delete/<int:review_id>/', views.ajax_delete_review, name='ajax_delete_review'),
    path('ajax/event/<int:event_id>/create/', views.ajax_create_event_reviews, name='ajax-create-event-reviews'),
    path('api/event/<int:event_id>/participants/', views.get_review_participants_api, name='api-participants'),
    path('api/my-reviews/', views.get_my_reviews_json, name='get_my_reviews_json'),
    path('api/user/<int:user_id>/', views.get_user_reviews_json, name='get_user_reviews_json'),
]