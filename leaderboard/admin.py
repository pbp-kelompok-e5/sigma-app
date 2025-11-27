"""
Django Admin Configuration untuk Leaderboard Module
Mendefinisikan tampilan admin interface untuk model PointTransaction dan Achievement
"""

# Import admin module dari Django
from django.contrib import admin
# Import model-model yang akan didaftarkan ke admin
from .models import PointTransaction, Achievement


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    """
    Admin interface untuk model PointTransaction.
    Menampilkan list transaksi poin dengan filter dan search.
    """

    # Kolom yang ditampilkan di list view
    # Menampilkan: user, jenis aktivitas, jumlah poin, dan waktu transaksi
    list_display = ('user', 'activity_type', 'points', 'created_at')

    # Filter sidebar untuk memudahkan pencarian
    # Bisa filter berdasarkan jenis aktivitas dan tanggal
    list_filter = ('activity_type', 'created_at')

    # Field yang bisa dicari di search box
    # Bisa search berdasarkan username atau deskripsi transaksi
    search_fields = ('user__username', 'description')

    # Field yang read-only (tidak bisa diedit)
    # created_at otomatis diisi oleh Django, jadi tidak perlu diedit
    readonly_fields = ('created_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """
    Admin interface untuk model Achievement.
    Menampilkan list achievement dengan filter dan search.
    """

    # Kolom yang ditampilkan di list view
    # Menampilkan: user, kode achievement, judul, bonus poin, dan waktu didapat
    list_display = ('user', 'achievement_code', 'title', 'bonus_points', 'earned_at')

    # Filter sidebar untuk memudahkan pencarian
    # Bisa filter berdasarkan kode achievement dan tanggal
    list_filter = ('achievement_code', 'earned_at')

    # Field yang bisa dicari di search box
    # Bisa search berdasarkan username atau judul achievement
    search_fields = ('user__username', 'title')

    # Field yang read-only (tidak bisa diedit)
    # earned_at otomatis diisi oleh Django, jadi tidak perlu diedit
    readonly_fields = ('earned_at',)
