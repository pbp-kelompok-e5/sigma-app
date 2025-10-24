from django.contrib import admin
from .models import PointTransaction, Achievement


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'points', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_code', 'title', 'bonus_points', 'earned_at')
    list_filter = ('achievement_code', 'earned_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('earned_at',)
