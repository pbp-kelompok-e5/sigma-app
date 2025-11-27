"""
App Configuration untuk Leaderboard Module
"""

# Import AppConfig dari Django
from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    """
    Konfigurasi aplikasi Leaderboard.
    Mendefinisikan nama aplikasi dan mengaktifkan signals.
    """

    # Field type default untuk auto-generated primary key
    default_auto_field = 'django.db.models.BigAutoField'

    # Nama aplikasi (harus sama dengan nama folder)
    name = 'leaderboard'

    def ready(self):
        """
        Method yang dipanggil ketika aplikasi siap.
        Digunakan untuk import signals agar signal handlers teregistrasi.

        PENTING: Import signals di sini, bukan di __init__.py
        Ini memastikan signals hanya diimport sekali saat aplikasi ready.
        """
        # Import signals untuk mengaktifkan signal handlers
        # Signal handlers akan otomatis listen ke perubahan di model lain
        import leaderboard.signals
