from datetime import date, time
from .models import Event, EventParticipant
from django.test import TestCase
from sigma_app.constants import SPORT_CHOICES, CITY_CHOICES
from django.contrib.auth.models import User

# Create your tests here.
class EventModelTest(TestCase):
    # Set-Up Events
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.event = Event.objects.create(
            organizer=self.user,
            title='Renang Relay',
            description='aiueo',
            sport_type='swimming',
            event_date=date(2025, 10, 24),
            start_time=time(14, 0),
            end_time=time(16, 0),
            city='semarang',
            location_name='Undip',
            max_participants=6,
        )

    def test_event_str_representation(self):
        self.assertEqual(str(self.event), 'Renang Relay')
        
    def test_event_is_full_function(self):
        self.assertFalse(self.event.is_full())
        self.event.current_participants = 6
        self.event.save()
        self.assertTrue(self.event.is_full())
        
    def test_event_default_status_open(self):
        self.assertEqual(self.event.status, 'open')

class EventParticipantModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.event = Event.objects.create(
            organizer=self.user,
            title='Renang Relay',
            description='aiueo',
            sport_type='swimming',
            event_date=date(2025, 10, 24),
            start_time=time(14, 0),
            end_time=time(16, 0),
            city='semarang',
            location_name='Undip',
            max_participants=6,
        )
        self.participant = EventParticipant.objects.create(
            event=self.event,
            user=self.user
        )
        
    def test_participant_str_representation(self):
        expected = f"{self.user.username} - {self.event.title}"
        self.assertEqual(str(self.participant), expected)
        
    def test_default_status(self):
        self.assertEqual(self.participant.status, 'joined')
    
        

    
