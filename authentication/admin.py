# Import Django admin module
from django.contrib import admin
# Import model-model dari aplikasi authentication
from .models import UserProfile, SportPreference


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface untuk model UserProfile.
    Mengatur tampilan dan fungsionalitas UserProfile di Django Admin.
    """

    # Field yang ditampilkan di list view (tabel)
    list_display = ('full_name', 'user', 'city', 'total_points', 'total_events', 'created_at')

    # Filter yang tersedia di sidebar untuk memfilter data
    list_filter = ('city', 'created_at', 'total_points')

    # Field yang bisa dicari menggunakan search box
    # Bisa mencari berdasarkan full_name, username, email, atau bio
    search_fields = ('full_name', 'user__username', 'user__email', 'bio')

    # Field yang tidak bisa diedit (read-only)
    # created_at, total_points, dan total_events tidak boleh diedit manual
    readonly_fields = ('created_at', 'total_points', 'total_events')

    # Fieldsets untuk mengorganisir field di detail view
    fieldsets = (
        # Section 1: Informasi User
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        # Section 2: Detail Profil
        ('Profile Details', {
            'fields': ('bio', 'city', 'profile_image_url')
        }),
        # Section 3: Statistik (collapsed by default)
        ('Statistics', {
            'fields': ('total_points', 'total_events'),
            'classes': ('collapse',)  # Collapsed by default
        }),
        # Section 4: Timestamps (collapsed by default)
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )

    def has_add_permission(self, request):
        """
        Override method untuk mencegah pembuatan UserProfile manual.
        UserProfile dibuat otomatis via signal ketika User dibuat.

        Returns:
            bool: False untuk mencegah tombol "Add" muncul di admin
        """
        return False


@admin.register(SportPreference)
class SportPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface untuk model SportPreference.
    Mengatur tampilan dan fungsionalitas SportPreference di Django Admin.
    """

    # Field yang ditampilkan di list view (tabel)
    list_display = ('user', 'sport_type', 'skill_level', 'created_at')

    # Filter yang tersedia di sidebar untuk memfilter data
    list_filter = ('sport_type', 'skill_level', 'created_at')

    # Field yang bisa dicari menggunakan search box
    # Bisa mencari berdasarkan username atau email user
    search_fields = ('user__username', 'user__email')

    # Field yang tidak bisa diedit (read-only)
    readonly_fields = ('created_at',)

    # Fieldsets untuk mengorganisir field di detail view
    fieldsets = (
        # Section 1: User & Sport
        ('User & Sport', {
            'fields': ('user', 'sport_type', 'skill_level')
        }),
        # Section 2: Timestamps (collapsed by default)
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)  # Collapsed by default
        }),
    )

    def get_queryset(self, request):
        """
        Override method untuk mengoptimasi query dengan select_related.
        Menghindari N+1 query problem ketika menampilkan list view.

        Returns:
            QuerySet: Queryset yang sudah dioptimasi dengan select_related
        """
        # Ambil queryset dari parent class
        queryset = super().get_queryset(request)
        # Tambahkan select_related untuk join dengan tabel User
        # Sehingga tidak perlu query terpisah untuk setiap user
        return queryset.select_related('user')
