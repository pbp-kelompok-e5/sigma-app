from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from reviews.models import Review, UserRating
from event_discovery.models import Event, EventParticipant
from django.utils import timezone


class BaseReviewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create 3 users
        self.author = User.objects.create_user(username="author", password="123")
        self.target = User.objects.create_user(username="target", password="123")
        self.other = User.objects.create_user(username="other", password="123")

        # Create event and participants
        self.event = Event.objects.create(
            organizer=self.author,
            title="Test Event",
            description="Test Desc",
            sport_type="Football",
            event_date=timezone.now().date(),
            start_time=timezone.now().time(),
            end_time=timezone.now().time(),
            city="Jakarta",
            location_name="Lapangan UI",
            max_participants=10,
            current_participants=2
        )

        # Event participants
        EventParticipant.objects.create(event=self.event, user=self.author, status="attended")
        EventParticipant.objects.create(event=self.event, user=self.target, status="attended")


class EventReviewsTest(BaseReviewTestCase):
    def test_get_event_reviews(self):
        self.client.force_login(self.author)
        url = reverse('reviews:event-reviews', args=[self.event.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "submit reviews")

    def test_post_bulk_review(self):
        self.client.force_login(self.author)
        url = reverse('reviews:event-reviews', args=[self.event.id])
        data = {
            f"rating_{self.target.id}": "5",
            f"comment_{self.target.id}": "Good player!"
        }
        res = self.client.post(url, data)
        self.assertEqual(Review.objects.count(), 1)
        self.assertRedirects(res, url)


class UserReviewsTest(BaseReviewTestCase):
    def test_user_reviews_page(self):
        Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")
        self.client.force_login(self.other)
        url = reverse('reviews:user-reviews', args=[self.target.id])
        res = self.client.get(url)
        self.assertContains(res, "Nice")


class UserWrittenReviewsTest(BaseReviewTestCase):
    def test_user_written_reviews_page(self):
        Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")
        self.client.force_login(self.other)
        url = reverse('reviews:user-written-reviews', args=[self.author.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Nice")


class EditReviewTest(BaseReviewTestCase):
    def test_author_can_edit(self):
        review = Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")
        self.client.force_login(self.author)
        url = reverse('reviews:edit-review', args=[review.id])
        res = self.client.post(url, {"rating": 3, "comment": "OK"})
        review.refresh_from_db()
        self.assertEqual(review.rating, 3)

    def test_other_cannot_edit(self):
        review = Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")
        self.client.force_login(self.other)
        url = reverse('reviews:edit-review', args=[review.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)  # redirected


class AjaxUpdateReviewTest(BaseReviewTestCase):
    def test_ajax_update(self):
        review = Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")

        self.client.force_login(self.author)
        url = reverse('reviews:ajax-update-review', args=[review.id])
        res = self.client.post(url, {"rating": 5, "comment": "Better!"})
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)


class AjaxDeleteReviewTest(BaseReviewTestCase):
    def test_ajax_delete(self):
        review = Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")

        self.client.force_login(self.author)
        url = reverse('reviews:ajax-delete-review', args=[review.id])
        res = self.client.post(url)
        self.assertEqual(Review.objects.count(), 0)


class AjaxCreateBulkReviewTest(BaseReviewTestCase):
    def test_ajax_bulk(self):
        self.client.force_login(self.author)
        url = reverse('reviews:ajax-create-event-reviews', args=[self.event.id])
        res = self.client.post(url, {f"rating_{self.target.id}": 5})
        self.assertEqual(Review.objects.count(), 1)


class RatingCalculationTest(BaseReviewTestCase):
    def test_update_user_rating(self):
        from reviews.views import update_user_rating
        Review.objects.create(event=self.event, from_user=self.author, to_user=self.target, rating=4, comment="Nice")
        Review.objects.create(event=self.event, from_user=self.other, to_user=self.target, rating=2, comment="Bad")

        update_user_rating(self.target)

        rating = UserRating.objects.get(user=self.target)
        self.assertEqual(float(rating.average_rating), 3.0)
        self.assertEqual(rating.total_reviews, 2)
        self.assertEqual(rating.four_star, 1)
        self.assertEqual(rating.two_star, 1)
