from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<uuid:event_id>/', views.event_reviews, name='event-reviews'),
]