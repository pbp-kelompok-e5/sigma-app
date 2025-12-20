from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from event_discovery.models import Event
from datetime import date, time
import json

class EventManagementAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def _event_data(self, **overrides):
        data = {
            "title": "API Friendly Match",
            "description": "Weekly futsal event for everyone, via API.",
            "sport_type": "football",
            "thumbnail": "",
            "event_date": date.today().isoformat(),
            "start_time": time(10, 0).isoformat(),
            "end_time": time(12, 0).isoformat(),
            "city": "jakarta_pusat",
            "location_name": "API Test Stadium",
            "max_participants": 20,
        }
        data.update(overrides)
        return data

    def test_create_event_api_success(self):
        url = reverse("event_management:api_create_event")
        data = self._event_data()
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().title, "API Friendly Match")

    def test_create_event_api_fail(self):
        url = reverse("event_management:api_create_event")
        data = self._event_data(title="")  # Invalid data
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertIn("title", response.json()["errors"])
        self.assertEqual(Event.objects.count(), 0)

    def test_cancel_event_api(self):
        # First, create an event to cancel
        event = Event.objects.create(
            organizer=self.user,
            **self._event_data(
                title="Cancellable Event",
                event_date=date.today(),
                start_time=time(14, 0),
                end_time=time(16, 0),
            )
        )
        self.assertEqual(event.status, "open")  # Initial status

        url = reverse("event_management:api_cancel_event", args=[event.id])
        response = self.client.post(url, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        event.refresh_from_db()
        self.assertEqual(event.status, "cancelled")
