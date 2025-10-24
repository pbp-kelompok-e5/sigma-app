from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from partner_matching.models import Connection
from partner_matching import views
from authentication.models import SportPreference, UserProfile


class PartnerMatchingTests(TestCase):
    def setUp(self):
        self.client = Client()
        # dua user untuk simulasi koneksi
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

        # Login user1
        self.client.login(username='alice', password='pass123')

    # Connection Request Tests
    def test_send_connection_request(self):
        """User1 mengirim request ke user2"""
        url = reverse('partner_matching:connection_request', args=['connect', self.user2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Connection.objects.filter(from_user=self.user1, to_user=self.user2, status='pending').exists())

    def test_cannot_send_request_to_self(self):
        """User tidak boleh connect dengan dirinya sendiri"""
        url = reverse('partner_matching:connection_request', args=['connect', self.user1.id])
        response = self.client.post(url)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Cannot connect', data['error'])

    def test_accept_connection_request(self):
        """User2 menerima permintaan koneksi dari user1"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='pending')
        self.client.logout()
        self.client.login(username='bob', password='pass123')
        url = reverse('partner_matching:connection_request', args=['accept', self.user1.id])
        response = self.client.post(url)
        data = response.json()
        self.assertTrue(data['success'])
        conn = Connection.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(conn.status, 'accepted')

    def test_reject_connection_request(self):
        """User2 menolak permintaan koneksi dari user1"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='pending')
        self.client.logout()
        self.client.login(username='bob', password='pass123')
        url = reverse('partner_matching:connection_request', args=['reject', self.user1.id])
        response = self.client.post(url)
        data = response.json()
        self.assertTrue(data['success'])
        conn = Connection.objects.get(from_user=self.user1, to_user=self.user2)
        self.assertEqual(conn.status, 'rejected')

    # connection_action_by_user Tests
    def test_remove_friend(self):
        """User menghapus teman setelah accepted"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='accepted')
        url = reverse('partner_matching:connection_action_by_user', args=['remove', self.user2.id])
        response = self.client.get(url)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(Connection.objects.exists())

    def test_cancel_sent_request(self):
        """User membatalkan permintaan koneksi yang belum diterima"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='pending')
        url = reverse('partner_matching:connection_action_by_user', args=['cancel', self.user2.id])
        response = self.client.get(url)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(Connection.objects.exists())

    # View protection and rendering
    def test_browse_user_requires_login(self):
        """Halaman browse_user hanya bisa diakses setelah login"""
        self.client.logout()
        url = reverse('partner_matching:browse_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect ke login

    def test_connections_view_success(self):
        """View connections merender halaman tanpa error"""
        url = reverse('partner_matching:connections')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partner_matching/connections.html')


class PartnerMatchingUtilsTests(TestCase):
    def setUp(self):
        # buat user
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

        # update profil bawaan
        profile1 = UserProfile.objects.get(user=self.user1)
        profile1.full_name = 'Alice'
        profile1.city = 'Jakarta'
        profile1.save()

        profile2 = UserProfile.objects.get(user=self.user2)
        profile2.full_name = 'Bob'
        profile2.city = 'Jakarta'
        profile2.save()

        # data sport preference
        SportPreference.objects.create(user=self.user1, sport_type='tennis', skill_level='beginner')
        SportPreference.objects.create(user=self.user1, sport_type='soccer', skill_level='intermediate')

        SportPreference.objects.create(user=self.user2, sport_type='tennis', skill_level='intermediate')
        SportPreference.objects.create(user=self.user2, sport_type='basketball', skill_level='advanced')

    def test_get_common_sports(self):
        """get_common_sports harus menemukan irisan olahraga"""
        result = views.get_common_sports(self.user1, self.user2)
        self.assertEqual(result, ['tennis'])

    def test_calculate_skill_compatibility(self):
        """Tes perbedaan skill antar dua user"""
        common = ['tennis']
        result = views.calculate_skill_compatibility(self.user1, self.user2, common)
        self.assertEqual(result, 7)

    def test_calculate_match_score_same_city(self):
        """Skor meningkat karena kota sama dan olahraga cocok"""
        score = views.calculate_match_score(self.user1, self.user2)
        self.assertTrue(score >= 47)

    def test_calculate_match_score_different_city(self):
        """Skor menurun kalau beda kota"""
        profile2 = UserProfile.objects.get(user=self.user2)
        profile2.city = 'Bandung'
        profile2.save()
        self.user2.refresh_from_db()

        score = views.calculate_match_score(self.user1, self.user2)
        self.assertEqual(score, 17)

class BrowseAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

        profile1 = UserProfile.objects.get(user=self.user1)
        profile1.city = 'Jakarta'
        profile1.save()

        profile2 = UserProfile.objects.get(user=self.user2)
        profile2.city = 'Bandung'
        profile2.save()

    def test_browse_user_ajax_returns_json(self):
        self.client.login(username='alice', password='pass123')
        url = reverse('partner_matching:browse_user_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json())

    def test_user_profile_detail_view(self):
        self.client.login(username='alice', password='pass123')
        url = reverse('partner_matching:user_profile', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user2.username)

class ExtraPartnerMatchingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.client.login(username='alice', password='pass123')

    def test_connection_request_requires_login(self):
        """Pastikan user harus login untuk mengirim connection request"""
        self.client.logout()
        url = reverse('partner_matching:connection_request', args=['connect', self.user2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # redirect ke login

    def test_connection_request_invalid_action(self):
        """Aksi invalid harus mengembalikan error"""
        url = reverse('partner_matching:connection_request', args=['invalid_action', self.user2.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid action', data['error'])

    def test_connection_action_invalid_status(self):
        """User mencoba menghapus koneksi yang belum accepted"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='pending')
        url = reverse('partner_matching:connection_action_by_user', args=['remove', self.user2.id])
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('No friendship found', data['error'])

    def test_browse_user_ajax_no_results(self):
        """browse_user_ajax tetap OK meskipun tidak ada hasil"""
        response = self.client.get(reverse('partner_matching:browse_user_api'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json())
        self.assertIsInstance(response.json()['users'], list)

    def test_public_connections_page_renders(self):
        """public_connections milik user lain dapat diakses"""
        Connection.objects.create(from_user=self.user1, to_user=self.user2, status='accepted')
        response = self.client.get(reverse('partner_matching:public_connections', args=[self.user2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partner_matching/connections.html')
