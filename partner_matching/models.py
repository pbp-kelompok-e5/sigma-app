from django.db import models
from django.contrib.auth.models import User

# Model untuk menyimpan koneksi pertemanan antar user
class Connection(models.Model):
    # Status koneksi, bisa pending, diterima, atau ditolak
    STATUS_CHOICES = [
        ('pending', 'Pending'),   # Permintaan koneksi dikirim tapi belum diterima
        ('accepted', 'Accepted'), # Permintaan koneksi diterima
        ('rejected', 'Rejected'), # Permintaan koneksi ditolak
    ]
    
    # User yang mengirim permintaan koneksi
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_sent')

    # User yang menerima permintaan koneksi
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_received')

    # Status koneksi, defaultnya pending
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Pesan opsional yang dikirim bersama permintaan koneksi
    message = models.TextField(blank=True, null=True)

    # Waktu pembuatan koneksi secara otomatis dicatat
    created_at = models.DateTimeField(auto_now_add=True)

    # Waktu update koneksi terakhir secara otomatis dicatat
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Kombinasi from_user dan to_user harus unik supaya tidak ada duplikat permintaan
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        # Representasi string menampilkan pengirim, penerima, dan status koneksi
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
