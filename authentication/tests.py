# Import TestCase dan Client untuk testing Django
from django.test import TestCase, Client
# Import model User bawaan Django
from django.contrib.auth.models import User
# Import reverse untuk mendapatkan URL dari nama URL pattern
from django.urls import reverse
# Import model-model dari aplikasi authentication
from .models import UserProfile, SportPreference
# Import form-form dari aplikasi authentication
from .forms import CustomUserCreationForm, UserProfileForm, SportPreferenceForm


class AuthenticationModelsTest(TestCase):
    """
    Test case untuk model-model di aplikasi authentication.
    Menguji UserProfile dan SportPreference model.
    """

    def setUp(self):
        """
        Setup yang dijalankan sebelum setiap test method.
        Membuat user untuk digunakan dalam testing.
        """
        # Buat user test dengan create_user (otomatis hash password)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_user_profile_creation(self):
        """
        Test bahwa UserProfile dibuat otomatis ketika User dibuat.
        Signal post_save seharusnya membuat UserProfile secara otomatis.
        """
        # Cek bahwa user memiliki atribut 'profile'
        self.assertTrue(hasattr(self.user, 'profile'))
        # Cek bahwa full_name di profile sesuai dengan first_name + last_name
        self.assertEqual(self.user.profile.full_name, 'Test User')

    def test_sport_preference_creation(self):
        """
        Test pembuatan sport preference.
        User seharusnya bisa membuat preferensi olahraga dengan sport_type dan skill_level.
        """
        # Buat sport preference untuk user
        preference = SportPreference.objects.create(
            user=self.user,
            sport_type='football',
            skill_level='intermediate'
        )
        # Cek bahwa preference tersimpan dengan benar
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.sport_type, 'football')
        self.assertEqual(preference.skill_level, 'intermediate')

    def test_sport_preference_unique_constraint(self):
        """
        Test constraint unique_together pada SportPreference.
        User tidak boleh memiliki duplikat sport_type yang sama.
        """
        # Buat sport preference pertama
        SportPreference.objects.create(
            user=self.user,
            sport_type='football',
            skill_level='intermediate'
        )

        # Coba buat sport preference kedua dengan sport_type yang sama
        # Seharusnya raise IntegrityError karena unique_together constraint
        with self.assertRaises(Exception):
            SportPreference.objects.create(
                user=self.user,
                sport_type='football',  # Duplikat sport_type
                skill_level='advanced'
            )


class AuthenticationViewsTest(TestCase):
    """
    Test case untuk views di aplikasi authentication.
    Menguji register, login, logout, dan profile views.
    """

    def setUp(self):
        """
        Setup yang dijalankan sebelum setiap test method.
        Membuat client dan user untuk testing.
        """
        # Buat test client untuk simulasi HTTP request
        self.client = Client()
        # Buat user test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_register_view_get(self):
        """
        Test register view dengan GET request.
        Seharusnya menampilkan form registrasi.
        """
        # GET request ke halaman register
        response = self.client.get(reverse('authentication:register'))
        # Cek status code 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Cek bahwa response mengandung teks 'Create your account'
        self.assertContains(response, 'Create your account')

    def test_register_view_post_valid(self):
        """
        Test register view dengan POST request dan data valid.
        Seharusnya membuat user baru dan redirect ke login.
        """
        # Data registrasi yang valid
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
        # POST request ke halaman register dengan data
        response = self.client.post(reverse('authentication:register'), data)
        # Cek status code 302 (redirect setelah registrasi sukses)
        self.assertEqual(response.status_code, 302)
        # Cek bahwa user baru telah dibuat di database
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """
        Test login view dengan GET request.
        Seharusnya menampilkan form login.
        """
        # GET request ke halaman login
        response = self.client.get(reverse('authentication:login'))
        # Cek status code 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Cek bahwa response mengandung teks 'Sign in to your account'
        self.assertContains(response, 'Sign in to your account')

    def test_login_view_post_valid(self):
        """
        Test login view dengan POST request dan kredensial valid.
        Seharusnya login user dan redirect ke profile.
        """
        # Data login yang valid
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        # POST request ke halaman login dengan data
        response = self.client.post(reverse('authentication:login'), data)
        # Cek status code 302 (redirect setelah login sukses)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated(self):
        """
        Test profile view ketika user sudah login.
        Seharusnya menampilkan halaman profil dengan nama user.
        """
        # Login user terlebih dahulu
        self.client.login(username='testuser', password='testpass123')
        # GET request ke halaman profile
        response = self.client.get(reverse('authentication:profile'))
        # Cek status code 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Cek bahwa response mengandung nama user
        self.assertContains(response, 'Test User')

    def test_profile_view_unauthenticated(self):
        """
        Test profile view ketika user belum login.
        Seharusnya redirect ke halaman login.
        """
        # GET request ke halaman profile tanpa login
        response = self.client.get(reverse('authentication:profile'))
        # Cek status code 302 (redirect ke login karena @login_required)
        self.assertEqual(response.status_code, 302)


class AuthenticationFormsTest(TestCase):
    """
    Test case untuk forms di aplikasi authentication.
    Menguji CustomUserCreationForm, UserProfileForm, dan SportPreferenceForm.
    """

    def test_custom_user_creation_form_valid(self):
        """
        Test CustomUserCreationForm dengan data yang valid.
        Form seharusnya valid jika semua field wajib diisi dengan benar.
        """
        # Data form yang valid
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
        # Buat instance form dengan data
        form = CustomUserCreationForm(data=form_data)
        # Cek bahwa form valid
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid_email(self):
        """
        Test CustomUserCreationForm dengan email yang tidak valid.
        Form seharusnya tidak valid dan ada error di field email.
        """
        # Data form dengan email yang tidak valid
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',  # Email tidak valid
            'first_name': 'Test',
            'last_name': 'User',
            'city': 'jakarta_pusat',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        # Buat instance form dengan data
        form = CustomUserCreationForm(data=form_data)
        # Cek bahwa form tidak valid
        self.assertFalse(form.is_valid())
        # Cek bahwa ada error di field email
        self.assertIn('email', form.errors)

    def test_sport_preference_form_valid(self):
        """
        Test SportPreferenceForm dengan data yang valid.
        Form seharusnya valid jika sport_type dan skill_level diisi dengan benar.
        """
        # Buat user untuk testing
        user = User.objects.create_user(username='testuser', password='testpass123')
        # Data form yang valid
        form_data = {
            'sport_type': 'football',
            'skill_level': 'intermediate'
        }
        # Buat instance form dengan data dan user
        form = SportPreferenceForm(data=form_data, user=user)
        # Cek bahwa form valid
        self.assertTrue(form.is_valid())
