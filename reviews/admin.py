from django.contrib import admin
from .models import Review, UserRating

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'from_user', 'to_user', 'rating', 'created_at')
    list_filter = ('rating', 'event')
    search_fields = ('from_user__username', 'to_user__username', 'event__title')
    autocomplete_fields = ('event', 'from_user', 'to_user')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'average_rating', 'total_reviews', 'last_updated')
    search_fields = ('user__username',)
    readonly_fields = (
        'average_rating', 
        'total_reviews',
        'five_star', 'four_star', 'three_star', 'two_star', 'one_star',
        'last_updated'
    )
