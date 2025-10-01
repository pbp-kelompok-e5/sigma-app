from django.db import models
from django.contrib.auth.models import User


# Model untuk menyimpan transaksi poin tiap user
class PointTransaction(models.Model):
    # Jenis aktivitas yang memberi atau mengurangi poin
    ACTIVITY_CHOICES = [
        ('event_join', 'Event Join'),             # Bergabung ke event
        ('event_complete', 'Event Complete'),     # Menyelesaikan event
        ('event_organize', 'Event Organize'),     # Menyelenggarakan event
        ('review_given', 'Review Given'),         # Memberi review
        ('five_star_received', 'Five Star Received'), # Mendapat review bintang lima
    ]
    
    # User yang mendapatkan transaksi poin
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')

    # Jenis aktivitas
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)

    # Jumlah poin yang diterima atau dikurangi
    points = models.IntegerField()

    # Deskripsi transaksi
    description = models.TextField()

    # Event yang terkait, bisa null atau kosong jika tidak terkait
    related_event = models.ForeignKey('event_discovery.Event', on_delete=models.SET_NULL, null=True, blank=True)

    # Waktu transaksi dibuat secara otomatis
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Representasi string menampilkan username, aktivitas, dan poin
        return f"{self.user.username} - {self.activity_type} (+{self.points})"


# Model untuk menyimpan peringkat leaderboard user
class Leaderboard(models.Model):
    # Periode leaderboard
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    # User yang masuk leaderboard
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')

    # Peringkat user dalam periode dan sport tertentu
    rank = models.IntegerField()

    # Total poin user dalam periode tersebut
    total_points = models.IntegerField()

    # Periode leaderboard
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)

    # Bisa ditentukan untuk olahraga tertentu, atau kosong jika umum
    sport_type = models.CharField(max_length=20, blank=True, null=True)

    # Waktu update terakhir secara otomatis
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Kombinasi user, periode, dan sport_type harus unik
        unique_together = ['user', 'period', 'sport_type']

        # Default pengurutan berdasarkan peringkat
        ordering = ['rank']
    
    def __str__(self):
        # Representasi string menampilkan peringkat, username, dan total poin
        return f"#{self.rank} - {self.user.username} ({self.total_points} pts)"


# Model untuk menyimpan prestasi atau achievement user
class Achievement(models.Model):
    # Kode prestasi yang bisa dicapai user
    ACHIEVEMENT_CODES = [
        ('first_event', 'First Event'),       # Mengikuti event pertama
        ('ten_events', '10 Events'),          # Mengikuti 10 event
        ('organizer', 'Organizer'),           # Menjadi penyelenggara event
        ('highly_rated', 'Highly Rated'),     # Mendapat rating tinggi
        ('social_butterfly', 'Social Butterfly'), # Aktif berinteraksi sosial
        ('early_bird', 'Early Bird'),         # Bergabung lebih awal
    ]
    
    # User yang mendapatkan achievement
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')

    # Kode achievement
    achievement_code = models.CharField(max_length=20, choices=ACHIEVEMENT_CODES)

    # Judul achievement
    title = models.CharField(max_length=100)

    # Deskripsi achievement
    description = models.TextField()

    # Bonus poin yang diberikan saat achievement diperoleh
    bonus_points = models.IntegerField(default=0)

    # Waktu pencapaian dicatat secara otomatis
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Kombinasi user dan achievement_code harus unik supaya tidak duplikat
        unique_together = ['user', 'achievement_code']
    
    def __str__(self):
        # Representasi string menampilkan username dan judul achievement
        return f"{self.user.username} - {self.title}"