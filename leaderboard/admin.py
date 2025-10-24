from django.contrib import admin
from .models import PointTransaction, Leaderboard, Achievement


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'points', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('rank', 'user', 'total_points', 'period', 'sport_type')
    list_filter = ('period', 'sport_type')
    search_fields = ('user__username',)
    readonly_fields = ('last_updated',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_code', 'title', 'bonus_points', 'earned_at')
    list_filter = ('achievement_code', 'earned_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('earned_at',)
