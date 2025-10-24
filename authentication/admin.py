from django.contrib import admin
from .models import UserProfile, SportPreference


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""

    list_display = ('full_name', 'user', 'city', 'total_points', 'total_events', 'created_at')
    list_filter = ('city', 'created_at', 'total_points')
    search_fields = ('full_name', 'user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'total_points', 'total_events')

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        ('Profile Details', {
            'fields': ('bio', 'city', 'profile_image_url')
        }),
        ('Statistics', {
            'fields': ('total_points', 'total_events'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of UserProfile (created via signal)"""
        return False


@admin.register(SportPreference)
class SportPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for SportPreference model"""

    list_display = ('user', 'sport_type', 'skill_level', 'created_at')
    list_filter = ('sport_type', 'skill_level', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('User & Sport', {
            'fields': ('user', 'sport_type', 'skill_level')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
