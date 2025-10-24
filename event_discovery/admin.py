from django.contrib import admin
from .models import Event, EventParticipant

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'sport_type', 'event_date', 'city', 'status')
    search_fields = ('title', 'city', 'sport_type')
    list_filter = ('sport_type', 'city', 'status')

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'joined_at')
    search_fields = ('event__title', 'user__username')
    list_filter = ('status', 'joined_at')