from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Model untuk menyimpan review atau rating dari satu user ke user lain setelah event
class Review(models.Model):
    # Event yang direview
    event = models.ForeignKey('event_discovery.Event', on_delete=models.CASCADE, related_name='reviews')

    # User yang memberikan review
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')

    # User yang menerima review
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')

    # Rating dari 1 sampai 5 bintang
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Komentar review
    comment = models.TextField()

    # Waktu review dibuat dan diupdate secara otomatis
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Satu user hanya boleh memberi satu review untuk user lain di satu event
        unique_together = ['event', 'from_user', 'to_user']
    
    def __str__(self):
        # Representasi string menampilkan pengirim, penerima, dan rating
        return f"{self.from_user.username} -> {self.to_user.username} ({self.rating}⭐)"


# Model untuk menyimpan ringkasan rating user secara keseluruhan
class UserRating(models.Model):
    # Relasi one-to-one dengan User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rating_summary')

    # Rata-rata rating user
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    # Total review yang diterima
    total_reviews = models.IntegerField(default=0)

    # Jumlah review per bintang
    five_star = models.IntegerField(default=0)
    four_star = models.IntegerField(default=0)
    three_star = models.IntegerField(default=0)
    two_star = models.IntegerField(default=0)
    one_star = models.IntegerField(default=0)

    # Waktu update terakhir secara otomatis
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # Representasi string menampilkan username dan rata-rata rating
        return f"{self.user.username} - {self.average_rating}⭐"
