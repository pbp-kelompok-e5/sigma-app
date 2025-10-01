from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, SportPreference
from .forms import CustomUserCreationForm, UserProfileForm, SportPreferenceForm


class AuthenticationModelsTest(TestCase):
    """Test authentication models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.full_name, 'Test User')

    def test_sport_preference_creation(self):
        """Test creating sport preferences"""
        preference = SportPreference.objects.create(
            user=self.user,
            sport_type='football',
            skill_level='intermediate'
        )
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.sport_type, 'football')
        self.assertEqual(preference.skill_level, 'intermediate')

    def test_sport_preference_unique_constraint(self):
        """Test that user can't have duplicate sport preferences"""
        SportPreference.objects.create(
            user=self.user,
            sport_type='football',
            skill_level='intermediate'
        )

        # This should raise an IntegrityError due to unique_together constraint
        with self.assertRaises(Exception):
            SportPreference.objects.create(
                user=self.user,
                sport_type='football',
                skill_level='advanced'
            )


class AuthenticationViewsTest(TestCase):
    """Test authentication views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('authentication:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')

    def test_register_view_post_valid(self):
        """Test register view with valid data"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'city': 'jakarta_pusat',
            'bio': 'Test bio',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('authentication:register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in to your account')

    def test_login_view_post_valid(self):
        """Test login view with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('authentication:login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_profile_view_authenticated(self):
        """Test profile view when authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

    def test_profile_view_unauthenticated(self):
        """Test profile view when not authenticated"""
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AuthenticationFormsTest(TestCase):
    """Test authentication forms"""

    def test_custom_user_creation_form_valid(self):
        """Test CustomUserCreationForm with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'city': 'jakarta_pusat',
            'bio': 'Test bio',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid_email(self):
        """Test CustomUserCreationForm with invalid email"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
            'city': 'jakarta_pusat',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_sport_preference_form_valid(self):
        """Test SportPreferenceForm with valid data"""
        user = User.objects.create_user(username='testuser', password='testpass123')
        form_data = {
            'sport_type': 'football',
            'skill_level': 'intermediate'
        }
        form = SportPreferenceForm(data=form_data, user=user)
        self.assertTrue(form.is_valid())
