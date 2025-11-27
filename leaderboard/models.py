"""
Models untuk Leaderboard Module
Berisi model untuk tracking poin user dan achievement/prestasi
"""

# Import model dan fungsi Django yang diperlukan
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PointTransaction(models.Model):
    """
    Model untuk menyimpan transaksi poin tiap user.
    Setiap aktivitas user yang menghasilkan poin akan dicatat di sini.

    Relasi:
    - ForeignKey ke User: Satu user bisa punya banyak transaksi poin
    - ForeignKey ke Event: Satu transaksi bisa terkait dengan satu event (opsional)
    """

    # Pilihan jenis aktivitas yang memberi atau mengurangi poin
    # Setiap tuple berisi (value_di_database, label_untuk_display)
    ACTIVITY_CHOICES = [
        ('event_join', 'Event Join'),             # User bergabung ke event (+10 poin)
        ('event_complete', 'Event Complete'),     # User menyelesaikan/hadir di event (+30 poin)
        ('event_organize', 'Event Organize'),     # User menyelenggarakan event (+50 poin)
        ('review_given', 'Review Given'),         # User memberi review ke user lain (+5 poin)
        ('five_star_received', 'Five Star Received'), # User mendapat review bintang 5 (+10 poin)
    ]

    # User yang mendapatkan transaksi poin
    # on_delete=CASCADE: Jika user dihapus, semua transaksi poinnya juga dihapus
    # related_name: Untuk akses reverse relation dari User ke PointTransaction
    # Contoh: user.point_transactions.all()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')

    # Jenis aktivitas yang menghasilkan poin
    # max_length=20: Panjang maksimal string
    # choices: Membatasi pilihan hanya dari ACTIVITY_CHOICES
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)

    # Jumlah poin yang diterima atau dikurangi
    # IntegerField: Bisa positif (dapat poin) atau negatif (kurang poin)
    points = models.IntegerField()

    # Deskripsi transaksi untuk memberikan konteks
    # Contoh: "Joined event: Badminton Tournament"
    description = models.TextField()

    # Event yang terkait dengan transaksi ini (opsional)
    # on_delete=SET_NULL: Jika event dihapus, field ini jadi NULL (transaksi tetap ada)
    # null=True, blank=True: Field ini boleh kosong
    related_event = models.ForeignKey('event_discovery.Event', on_delete=models.SET_NULL, null=True, blank=True)

    # Waktu transaksi dibuat
    # auto_now_add=True: Otomatis diisi dengan waktu saat record dibuat
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordering default: Transaksi terbaru di atas
        # '-created_at' berarti descending (terbaru dulu)
        ordering = ['-created_at']

    def __str__(self):
        """
        Representasi string untuk ditampilkan di admin atau debugging.
        Format: "username - activity_type (+points)"
        Contoh: "john_doe - event_join (+10)"
        """
        return f"{self.user.username} - {self.activity_type} (+{self.points})"


class Achievement(models.Model):
    """
    Model untuk menyimpan prestasi atau achievement yang dicapai user.
    Achievement diberikan otomatis ketika user mencapai milestone tertentu.

    Relasi:
    - ForeignKey ke User: Satu user bisa punya banyak achievement

    Constraint:
    - unique_together: Satu user tidak bisa dapat achievement yang sama dua kali
    """

    # Kode prestasi yang bisa dicapai user
    # Setiap tuple berisi (code, display_name)
    ACHIEVEMENT_CODES = [
        ('first_event', 'First Event'),       # Mengikuti event pertama kali
        ('ten_events', '10 Events'),          # Menyelesaikan 10 event
        ('organizer', 'Organizer'),           # Menyelenggarakan 5 event
        ('highly_rated', 'Highly Rated'),     # Mendapat 10 review bintang 5
        ('social_butterfly', 'Social Butterfly'), # Membuat 20 koneksi (belum diimplementasi)
        ('early_bird', 'Early Bird'),         # Bergabung 5 event pagi (belum diimplementasi)
    ]

    # User yang mendapatkan achievement
    # on_delete=CASCADE: Jika user dihapus, semua achievementnya juga dihapus
    # related_name: Untuk akses reverse relation dari User ke Achievement
    # Contoh: user.achievements.all()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')

    # Kode achievement yang dicapai
    # max_length=20: Panjang maksimal string
    # choices: Membatasi pilihan hanya dari ACHIEVEMENT_CODES
    achievement_code = models.CharField(max_length=20, choices=ACHIEVEMENT_CODES)

    # Judul achievement yang ditampilkan ke user
    # Contoh: "🏃 First Event"
    title = models.CharField(max_length=100)

    # Deskripsi achievement untuk memberikan konteks
    # Contoh: "Joined your first event"
    description = models.TextField()

    # Bonus poin yang diberikan saat achievement diperoleh
    # default=0: Jika tidak diisi, default 0
    # Bonus poin ini akan ditambahkan ke total_points user via PointTransaction
    bonus_points = models.IntegerField(default=0)

    # Waktu pencapaian dicatat
    # auto_now_add=True: Otomatis diisi dengan waktu saat achievement diperoleh
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Kombinasi user dan achievement_code harus unik
        # Ini mencegah user mendapat achievement yang sama lebih dari sekali
        unique_together = ['user', 'achievement_code']

        # Ordering default: Achievement terbaru di atas
        ordering = ['-earned_at']

    def __str__(self):
        """
        Representasi string untuk ditampilkan di admin atau debugging.
        Format: "username - title"
        Contoh: "john_doe - 🏃 First Event"
        """
        return f"{self.user.username} - {self.title}"


# ===== DJANGO SIGNALS =====
# Signal untuk otomatis update total_points di UserProfile

@receiver(post_save, sender=PointTransaction)
def update_user_points(sender, instance, created, **kwargs):
    """
    Signal handler untuk update total points di UserProfile.
    Dipanggil otomatis setiap kali PointTransaction baru dibuat.

    Args:
        sender: Model class yang mengirim signal (PointTransaction)
        instance: Instance PointTransaction yang baru dibuat
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True)
    2. Ambil UserProfile dari user yang terkait
    3. Hitung total poin dari semua PointTransaction user
    4. Update field total_points di UserProfile
    5. Save UserProfile
    """
    # Hanya proses jika ini record baru (bukan update)
    if created:
        # Import UserProfile di dalam fungsi untuk menghindari circular import
        from authentication.models import UserProfile

        try:
            # Ambil UserProfile dari user yang terkait dengan transaksi ini
            profile = UserProfile.objects.get(user=instance.user)

            # Hitung total poin dari semua transaksi user
            # aggregate(Sum('points')) mengembalikan dict: {'points__sum': total}
            # or 0: Jika belum ada transaksi, gunakan 0
            total = PointTransaction.objects.filter(user=instance.user).aggregate(
                models.Sum('points')
            )['points__sum'] or 0

            # Update total_points di UserProfile
            profile.total_points = total

            # Simpan perubahan ke database
            profile.save()

        except UserProfile.DoesNotExist:
            # Jika UserProfile belum ada, skip (tidak perlu error)
            # Ini adalah edge case yang seharusnya tidak terjadi karena
            # UserProfile dibuat otomatis via signal saat User dibuat
            pass