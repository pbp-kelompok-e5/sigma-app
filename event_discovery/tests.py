from datetime import date, time

from django.urls import reverse
from .models import Event, EventParticipant
from django.test import Client, TestCase
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
    

class EventDiscoveryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

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
            current_participants=0,
            status='open'
        )

    def test_show_event_template(self):
        response = self.client.get(reverse('event_discovery:show_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_page.html')

    def test_show_json_returns_event_list(self):
        response = self.client.get(reverse('event_discovery:show_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['title'], 'Renang Relay')

    def test_show_json_by_id(self):
        response = self.client.get(reverse('event_discovery:show_json_by_id', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], str(self.event.id))

    def test_show_my_event_template(self):
        response = self.client.get(reverse('event_discovery:show_my_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_my.html')

    def test_show_json_my_event_empty(self):
        response = self.client.get(reverse('event_discovery:show_json_my_event'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_join_event_success(self):
        response = self.client.post(reverse('event_discovery:join_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(EventParticipant.objects.count(), 1)
        self.event.refresh_from_db()
        self.assertEqual(self.event.current_participants, 1)

    def test_join_event_full(self):
        self.event.current_participants = 6
        self.event.save()
        response = self.client.post(reverse('event_discovery:join_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 400)

    def test_join_event_duplicate(self):
        EventParticipant.objects.create(user=self.user, event=self.event)
        self.event.current_participants = 1
        self.event.save()
        response = self.client.post(reverse('event_discovery:join_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 400)

    def test_leave_event_success(self):
        EventParticipant.objects.create(user=self.user, event=self.event)
        self.event.current_participants = 1
        self.event.save()
        response = self.client.post(reverse('event_discovery:leave_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(EventParticipant.objects.count(), 0)
        self.event.refresh_from_db()
        self.assertEqual(self.event.current_participants, 0)

    def test_leave_event_not_joined(self):
        response = self.client.post(reverse('event_discovery:leave_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 404)

    def test_event_detail_template(self):
        response = self.client.get(reverse('event_discovery:event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')

    def test_event_participant_status_joined(self):
        EventParticipant.objects.create(user=self.user, event=self.event)
        response = self.client.get(reverse('event_discovery:event_participant_status', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'joined')

    def test_event_participant_status_not_participating(self):
        response = self.client.get(reverse('event_discovery:event_participant_status', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'not_participating')

    def test_anonymous_user_cannot_join(self):
        self.client.logout()
        response = self.client.post(reverse('event_discovery:join_event', args=[self.event.id]))
        self.assertEqual(response.status_code, 400)  # or 401 if you add an auth check
