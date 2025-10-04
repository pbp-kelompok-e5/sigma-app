from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sigma_app.constants import CITY_CHOICES, SPORT_CHOICES, SKILL_CHOICES


# Model tambahan untuk menyimpan profil user (melengkapi User bawaan Django)
class UserProfile(models.Model):
    # Hubungan one-to-one dengan model User bawaan Django
    # related_name='profile' → bisa diakses lewat user.profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Nama lengkap user
    full_name = models.CharField(max_length=100)
    
    # Deskripsi singkat (opsional, bisa kosong/null)
    bio = models.TextField(blank=True, null=True)

    # Lokasi user (pilihan dari daftar CITY_CHOICES)
    city = models.CharField(max_length=50, choices=CITY_CHOICES)

    # URL gambar profil user (opsional, user akan memberikan URL)
    profile_image_url = models.URLField(blank=True, null=True)

    # Total poin user (misal dari leaderboard / aktivitas event)
    total_points = models.IntegerField(default=0)

    # Jumlah event yang pernah diikuti user
    total_events = models.IntegerField(default=0)

    # Tanggal pembuatan profile
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


# Model untuk menyimpan preferensi olahraga tiap user
class SportPreference(models.Model):
    # Relasi many-to-one → 1 user bisa punya banyak preferensi olahraga
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sport_preferences')

    # Jenis olahraga (pilihan dari SPORT_CHOICES)
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)

    # Tingkat skill user di olahraga tersebut (beginner/intermediate/expert, dsb)
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES)

    # Tanggal preferensi dibuat
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Satu user tidak boleh punya duplikat sport_type yang sama
        unique_together = ['user', 'sport_type']

    def __str__(self):
        return f"{self.user.username} - {self.sport_type}"


# Signal untuk otomatis membuat UserProfile ketika User baru dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance, 
            full_name=instance.get_full_name() or instance.username
        )


# Signal untuk menyimpan perubahan pada User sekaligus update UserProfile
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Cek dulu apakah user sudah punya profile
    if hasattr(instance, 'profile'):
        instance.profile.save()