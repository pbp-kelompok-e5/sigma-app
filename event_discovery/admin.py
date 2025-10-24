from django.contrib import admin
from .models import Event

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'sport_type', 'event_date', 'city', 'status')
    search_fields = ('title', 'city', 'sport_type')
    list_filter = ('sport_type', 'city', 'status')
