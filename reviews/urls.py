from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:event_id>/', views.event_reviews, name='event-reviews'),
    path('user/<int:user_id>/', views.user_reviews, name='user-reviews'),
]