from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from event_discovery.models import Event
from datetime import date, time

class EventManagementAjaxTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="arief", password="pass123")
        self.client.login(username="arief", password="pass123")

    def _event_data(self, **overrides):
        data = {
            "title": "Friendly Match",
            "description": "Weekly futsal event for everyone.",
            "thumbnail": "https://example.com/futsal.jpg",
            "sport_type": "football",  # from SPORT_CHOICES
            "event_date": date.today(),
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "city": "Jakarta",
            "location_name": "GBK Stadium",
            "max_participants": 10,
        }
        data.update(overrides)
        return data

    def test_create_event_ajax(self):
        url = reverse("event_management:create_event")
        response = self.client.post(
            url, self._event_data(), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        print("Response JSON:", response.json())
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json()["success"])
        self.assertEqual(Event.objects.count(), 1)

    def test_update_event_ajax(self):
        event = Event.objects.create(
            **self._event_data(title="Old Event"), organizer=self.user
        )
        url = reverse("event_management:update_event", args=[event.id])
        response = self.client.post(
            url,
            self._event_data(title="Updated Event"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        event.refresh_from_db()
        self.assertEqual(event.title, "Updated Event")

    def test_delete_event_ajax(self):
        event = Event.objects.create(
            **self._event_data(title="Delete Me"), organizer=self.user
        )
        url = reverse("event_management:delete_event", args=[event.id])
        response = self.client.delete(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(id=event.id).exists())

    def test_cancel_event_ajax(self):
        event = Event.objects.create(
            **self._event_data(title="Cancelable Event"), organizer=self.user
        )
        url = reverse("event_management:cancel_event", args=[event.id])
        response = self.client.patch(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.status, "cancelled")
