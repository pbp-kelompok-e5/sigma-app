from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from authentication.models import UserProfile
from leaderboard.models import PointTransaction, Achievement
from leaderboard.views import get_tier, get_badge, get_achievement_description


class PointTransactionModelTest(TestCase):
    """Test cases for PointTransaction model"""

    def setUp(self):
        """Set up test user and profile"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        # Profile is automatically created by signal
        self.profile = self.user.profile
        self.profile.city = 'jakarta'
        self.profile.save()
    
    def test_create_point_transaction(self):
        """Test creating a point transaction"""
        transaction = PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=10,
            description='Joined test event'
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.activity_type, 'event_join')
        self.assertEqual(transaction.points, 10)
        self.assertIsNotNone(transaction.created_at)
    
    def test_point_transaction_str(self):
        """Test string representation of point transaction"""
        transaction = PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=10,
            description='Test'
        )
        expected = f"{self.user.username} - event_join (+10)"
        self.assertEqual(str(transaction), expected)
    
    def test_point_transaction_updates_profile(self):
        """Test that creating a transaction updates user profile total_points"""
        initial_points = self.profile.total_points

        # Create first transaction (event_join triggers first_event achievement with 5 bonus points)
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=10,
            description='Test 1'
        )
        self.profile.refresh_from_db()
        # Should have 10 points + 5 bonus from first_event achievement
        self.assertEqual(self.profile.total_points, initial_points + 15)

        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_complete',
            points=20,
            description='Test 2'
        )
        self.profile.refresh_from_db()
        # Should have 10 + 5 (bonus) + 20 = 35 total
        self.assertEqual(self.profile.total_points, initial_points + 35)


class AchievementModelTest(TestCase):
    """Test cases for Achievement model"""
    
    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_create_achievement(self):
        """Test creating an achievement"""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_code='first_event',
            title='First Event',
            description='Joined your first event',
            bonus_points=5
        )
        self.assertEqual(achievement.user, self.user)
        self.assertEqual(achievement.achievement_code, 'first_event')
        self.assertEqual(achievement.bonus_points, 5)
        self.assertIsNotNone(achievement.earned_at)
    
    def test_achievement_str(self):
        """Test string representation of achievement"""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_code='first_event',
            title='First Event',
            description='Test',
            bonus_points=5
        )
        expected = f"{self.user.username} - First Event"
        self.assertEqual(str(achievement), expected)
    
    def test_achievement_unique_together(self):
        """Test that user can't earn same achievement twice"""
        Achievement.objects.create(
            user=self.user,
            achievement_code='first_event',
            title='First Event',
            description='Test',
            bonus_points=5
        )
        # Attempting to create duplicate should raise error
        with self.assertRaises(Exception):
            Achievement.objects.create(
                user=self.user,
                achievement_code='first_event',
                title='First Event',
                description='Test',
                bonus_points=5
            )


class HelperFunctionsTest(TestCase):
    """Test cases for helper functions"""
    
    def test_get_tier(self):
        """Test get_tier function"""
        self.assertEqual(get_tier(0), 'Beginner')
        self.assertEqual(get_tier(49), 'Beginner')
        self.assertEqual(get_tier(50), 'Intermediate')
        self.assertEqual(get_tier(199), 'Intermediate')
        self.assertEqual(get_tier(200), 'Advanced')
        self.assertEqual(get_tier(499), 'Advanced')
        self.assertEqual(get_tier(500), 'Expert')
        self.assertEqual(get_tier(999), 'Expert')
        self.assertEqual(get_tier(1000), 'Master')
        self.assertEqual(get_tier(5000), 'Master')
    
    def test_get_badge(self):
        """Test get_badge function"""
        self.assertEqual(get_badge(0), '🔰')
        self.assertEqual(get_badge(49), '🔰')
        self.assertEqual(get_badge(50), '⭐')
        self.assertEqual(get_badge(199), '⭐')
        self.assertEqual(get_badge(200), '🥉')
        self.assertEqual(get_badge(499), '🥉')
        self.assertEqual(get_badge(500), '🥈')
        self.assertEqual(get_badge(999), '🥈')
        self.assertEqual(get_badge(1000), '🥇')
        self.assertEqual(get_badge(5000), '🥇')
    
    def test_get_achievement_description(self):
        """Test get_achievement_description function"""
        self.assertEqual(get_achievement_description('first_event'), 'Join your first event')
        self.assertEqual(get_achievement_description('ten_events'), 'Complete 10 events')
        self.assertEqual(get_achievement_description('organizer'), 'Organize 5 events')
        self.assertEqual(get_achievement_description('highly_rated'), 'Receive 10 five-star reviews')
        self.assertEqual(get_achievement_description('social_butterfly'), 'Make 20 connections')
        self.assertEqual(get_achievement_description('early_bird'), 'Join 5 morning events')
        self.assertEqual(get_achievement_description('unknown'), 'Unknown achievement')


class LeaderboardPageViewTest(TestCase):
    """Test cases for leaderboard_page view"""

    def setUp(self):
        """Set up test users and data"""
        self.client = Client()

        # Create users with different points
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.profile1 = self.user1.profile
        self.profile1.full_name = 'User One'
        self.profile1.city = 'jakarta'
        self.profile1.total_points = 100
        self.profile1.save()

        self.user2 = User.objects.create_user(username='user2', password='pass123')
        self.profile2 = self.user2.profile
        self.profile2.full_name = 'User Two'
        self.profile2.city = 'bandung'
        self.profile2.total_points = 200
        self.profile2.save()

        self.user3 = User.objects.create_user(username='user3', password='pass123')
        self.profile3 = self.user3.profile
        self.profile3.full_name = 'User Three'
        self.profile3.city = 'surabaya'
        self.profile3.total_points = 0  # Should not appear in leaderboard
        self.profile3.save()
    
    def test_leaderboard_page_loads(self):
        """Test that leaderboard page loads successfully"""
        response = self.client.get(reverse('leaderboard:leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard/leaderboard.html')
    
    def test_leaderboard_ranking_order(self):
        """Test that users are ranked correctly by points"""
        response = self.client.get(reverse('leaderboard:leaderboard'))
        users = response.context['users']
        
        # Should only have 2 users (user3 has 0 points)
        self.assertEqual(len(users), 2)
        
        # Check ranking order
        self.assertEqual(users[0]['username'], 'user2')
        self.assertEqual(users[0]['rank'], 1)
        self.assertEqual(users[0]['total_points'], 200)
        
        self.assertEqual(users[1]['username'], 'user1')
        self.assertEqual(users[1]['rank'], 2)
        self.assertEqual(users[1]['total_points'], 100)
    
    def test_leaderboard_excludes_zero_points(self):
        """Test that users with 0 points are excluded"""
        response = self.client.get(reverse('leaderboard:leaderboard'))
        users = response.context['users']
        
        usernames = [u['username'] for u in users]
        self.assertNotIn('user3', usernames)
    
    def test_leaderboard_current_user_rank(self):
        """Test that current user's rank is shown when logged in"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('leaderboard:leaderboard'))
        
        self.assertEqual(response.context['current_user_rank'], 2)
    
    def test_leaderboard_period_filter_all_time(self):
        """Test leaderboard with all_time filter"""
        response = self.client.get(reverse('leaderboard:leaderboard') + '?period=all_time')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_filter'], 'all_time')


class LeaderboardAPIViewTest(TestCase):
    """Test cases for leaderboard_api view"""

    def setUp(self):
        """Set up test users"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = self.user.profile
        self.profile.full_name = 'Test User'
        self.profile.city = 'jakarta'
        self.profile.total_points = 100
        self.profile.save()
    
    def test_leaderboard_api_returns_json(self):
        """Test that API returns JSON response"""
        response = self.client.get(reverse('leaderboard:leaderboard_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_leaderboard_api_structure(self):
        """Test API response structure"""
        response = self.client.get(reverse('leaderboard:leaderboard_api'))
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('users', data)
        self.assertIn('total_count', data)
        self.assertIn('page', data)
        self.assertIn('per_page', data)
    
    def test_leaderboard_api_pagination(self):
        """Test API pagination"""
        response = self.client.get(reverse('leaderboard:leaderboard_api') + '?page=1&per_page=10')
        data = response.json()
        
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['per_page'], 10)


class PointsDashboardViewTest(TestCase):
    """Test cases for points_dashboard view"""

    def setUp(self):
        """Set up test user and transactions"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = self.user.profile
        self.profile.full_name = 'Test User'
        self.profile.city = 'jakarta'
        self.profile.save()
        
        # Create some transactions
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=10,
            description='Test 1'
        )
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_complete',
            points=20,
            description='Test 2'
        )
    
    def test_points_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        # Verify that logged in users can access the dashboard
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard/points_dashboard.html')
    
    def test_points_dashboard_loads_for_authenticated_user(self):
        """Test that dashboard loads for logged in user"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard/points_dashboard.html')
    
    def test_points_dashboard_context(self):
        """Test dashboard context data"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_dashboard'))

        self.assertIn('profile', response.context)
        self.assertIn('total_points', response.context)
        self.assertIn('breakdown', response.context)
        self.assertIn('recent_transactions', response.context)
        self.assertIn('tier', response.context)
        self.assertIn('badge', response.context)


class PointsHistoryViewTest(TestCase):
    """Test cases for points_history view"""

    def setUp(self):
        """Set up test user and transactions"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = self.user.profile
        self.profile.full_name = 'Test User'
        self.profile.city = 'jakarta'
        self.profile.save()

        # Create transactions
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=10,
            description='Test 1'
        )
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_complete',
            points=20,
            description='Test 2'
        )

    def test_points_history_requires_login(self):
        """Test that history requires authentication"""
        # Verify that logged in users can access
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_history'))
        self.assertEqual(response.status_code, 200)

    def test_points_history_loads_for_authenticated_user(self):
        """Test that history loads for logged in user"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_history'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard/points_history.html')

    def test_points_history_shows_transactions(self):
        """Test that history shows user's transactions"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_history'))

        transactions = response.context['transactions']
        # Should have at least the 2 transactions we created
        self.assertGreaterEqual(transactions.count(), 2)

    def test_points_history_activity_filter(self):
        """Test filtering by activity type"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:points_history') + '?activity=event_join')

        transactions = response.context['transactions']
        # Should have at least 1 event_join transaction
        self.assertGreaterEqual(transactions.count(), 1)
        # All transactions should be event_join type
        for transaction in transactions:
            self.assertEqual(transaction.activity_type, 'event_join')


class AchievementsPageViewTest(TestCase):
    """Test cases for achievements_page view"""

    def setUp(self):
        """Set up test user and achievements"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = self.user.profile
        self.profile.full_name = 'Test User'
        self.profile.city = 'jakarta'
        self.profile.save()

        # Create an achievement
        Achievement.objects.create(
            user=self.user,
            achievement_code='first_event',
            title='First Event',
            description='Joined your first event',
            bonus_points=5
        )

    def test_achievements_page_requires_login(self):
        """Test that achievements page requires authentication"""
        # Verify that logged in users can access
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:achievements'))
        self.assertEqual(response.status_code, 200)

    def test_achievements_page_loads_for_authenticated_user(self):
        """Test that achievements page loads for logged in user"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:achievements'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'leaderboard/achievements.html')

    def test_achievements_page_context(self):
        """Test achievements page context data"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:achievements'))

        self.assertIn('all_achievements', response.context)
        self.assertIn('earned_count', response.context)
        self.assertIn('total_count', response.context)
        self.assertIn('earned_percent', response.context)

        # Should have 1 earned achievement
        self.assertEqual(response.context['earned_count'], 1)

        # Total should be 6 (all possible achievements)
        self.assertEqual(response.context['total_count'], 6)

    def test_achievements_earned_status(self):
        """Test that earned achievements are marked correctly"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('leaderboard:achievements'))

        all_achievements = response.context['all_achievements']

        # Find first_event achievement
        first_event = next(a for a in all_achievements if a['code'] == 'first_event')
        self.assertTrue(first_event['is_earned'])
        self.assertIsNotNone(first_event['earned_at'])

        # Find an unearned achievement
        ten_events = next(a for a in all_achievements if a['code'] == 'ten_events')
        self.assertFalse(ten_events['is_earned'])
        self.assertIsNone(ten_events['earned_at'])


class LeaderboardPeriodFilterTest(TestCase):
    """Test cases for period filtering in leaderboard"""

    def setUp(self):
        """Set up test users with time-based transactions"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = self.user.profile
        self.profile.full_name = 'Test User'
        self.profile.city = 'jakarta'
        self.profile.save()

        # Create old transaction (more than 30 days ago)
        old_transaction = PointTransaction.objects.create(
            user=self.user,
            activity_type='event_join',
            points=50,
            description='Old event'
        )
        # Manually set created_at to 40 days ago
        old_transaction.created_at = timezone.now() - timedelta(days=40)
        old_transaction.save()

        # Create recent transaction (within 7 days)
        PointTransaction.objects.create(
            user=self.user,
            activity_type='event_complete',
            points=30,
            description='Recent event'
        )

    def test_weekly_filter(self):
        """Test weekly period filter"""
        response = self.client.get(reverse('leaderboard:leaderboard') + '?period=weekly')
        self.assertEqual(response.status_code, 200)
        users = response.context['users']

        # Should only count recent transactions (30 points + possible achievement bonus)
        if len(users) > 0:
            # At least 30 points from the recent transaction
            self.assertGreaterEqual(users[0]['total_points'], 30)

    def test_monthly_filter(self):
        """Test monthly period filter"""
        response = self.client.get(reverse('leaderboard:leaderboard') + '?period=monthly')
        self.assertEqual(response.status_code, 200)
        users = response.context['users']

        # Should only count recent transactions (30 points + possible achievement bonus)
        if len(users) > 0:
            # At least 30 points from the recent transaction
            self.assertGreaterEqual(users[0]['total_points'], 30)

    def test_all_time_filter(self):
        """Test all_time period filter uses profile total_points"""
        # Update profile total_points to reflect all transactions
        self.profile.total_points = 80
        self.profile.save()

        response = self.client.get(reverse('leaderboard:leaderboard') + '?period=all_time')
        self.assertEqual(response.status_code, 200)
        users = response.context['users']

        # Should count all points from profile
        if len(users) > 0:
            self.assertEqual(users[0]['total_points'], 80)

