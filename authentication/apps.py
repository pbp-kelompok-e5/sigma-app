# Import AppConfig untuk konfigurasi aplikasi Django
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Konfigurasi untuk aplikasi authentication.
    Class ini mendefinisikan pengaturan dasar aplikasi.
    """

    # Tipe field auto-increment yang digunakan untuk primary key
    # BigAutoField mendukung integer yang lebih besar (64-bit)
    default_auto_field = 'django.db.models.BigAutoField'

    # Nama aplikasi (harus sama dengan nama folder)
    name = 'authentication'

    def ready(self):
        """
        Method yang dipanggil ketika aplikasi siap digunakan.
        Digunakan untuk registrasi signals dan setup lainnya.
        """
        # Import models untuk memastikan signals yang didefinisikan di models.py ter-register
        # Signal post_save untuk auto-create UserProfile akan aktif setelah import ini
        from . import models  # This will register the signals defined in models.py
