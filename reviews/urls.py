from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:event_id>/', views.event_reviews, name='event-reviews'),
    path('user/<int:user_id>/', views.user_reviews, name='user-reviews'),
    path('written/<int:user_id>/', views.user_written_reviews, name='user-written-reviews'),
    path('edit/<int:review_id>/', views.edit_review, name='edit-review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete-review'),
]