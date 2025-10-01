from django.db import models
from django.contrib.auth.models import User
from sigma_app.constants import SPORT_CHOICES

# Model untuk menyimpan informasi Event, yaitu kegiatan olahraga
class Event(models.Model):
    # Pilihan status event
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # User yang membuat atau menyelenggarakan event
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    
    # Judul dan deskripsi dari event
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Jenis olahraga yang dipilih dari SPORT_CHOICES
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)

    # Tanggal dan jam berlangsungnya event
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Lokasi event, termasuk kota dan nama tempat
    city = models.CharField(max_length=50)
    location_name = models.CharField(max_length=200)

    # Batasan jumlah peserta dan jumlah peserta saat ini
    max_participants = models.IntegerField()
    current_participants = models.IntegerField(default=0)
    
    # Status event, defaultnya open
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    # Tanggal pembuatan dan update terakhir event secara otomatis
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Representasi string menampilkan judul event
        return self.title
    
    def is_full(self):
        # Mengecek apakah jumlah peserta sudah mencapai batas maksimum
        return self.current_participants >= self.max_participants


# Model untuk menyimpan partisipasi user dalam sebuah event
class EventParticipant(models.Model):
    # Pilihan status partisipasi user
    STATUS_CHOICES = [
        ('joined', 'Joined'),       # User baru bergabung
        ('attended', 'Attended'),   # User hadir di event
        ('cancelled', 'Cancelled'), # User membatalkan partisipasi
    ]
    
    # Relasi ke Event, peserta (banyak) bisa ikut dalam satu event
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')

    # Relasi ke User, satu user bisa ikut banyak event
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='joined_events')

    # Status partisipasi, defaultnya joined
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')

    # Waktu saat user bergabung secara otomatis dicatat
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Satu user hanya boleh ikut satu kali dalam satu event
        unique_together = ['event', 'user']
    
    def __str__(self):
        # Representasi string menampilkan username dan judul event
        return f"{self.user.username} - {self.event.title}"
