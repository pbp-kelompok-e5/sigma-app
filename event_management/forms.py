from django import forms
from event_discovery.models import Event
from sigma_app.constants import CITY_CHOICES

class EventForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    city = forms.ChoiceField(
        choices=CITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'data-placeholder': 'Search and select your city'})
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'sport_type', 'thumbnail', 'event_date',
            'start_time', 'end_time', 'city', 'location_name',
            'max_participants',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter event title',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe your event in detail',
                'class': 'form-input'
            }),
            'sport_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'thumbnail': forms.URLInput(attrs={
                'placeholder': 'Enter event thumbnail image URL',
                'class': 'form-input'
            }),
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'city': forms.Select(attrs={
                'data-placeholder': 'Search and select your city',
                'class': 'form-input'
            }),
            'location_name': forms.TextInput(attrs={
                'placeholder': 'Enter event location name',
                'class': 'form-input'
            }),
            'max_participants': forms.NumberInput(attrs={
                'placeholder': 'Maximum number of participants',
                'class': 'form-input',
                'min': '1'
            }),
        }
        labels = {
            'title': 'Event Title',
            'description': 'Event Description',
            'sport_type': 'Sport Type',
            'thumbnail': 'Event Thumbnail URL',
            'event_date': 'Event Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'city': 'City',
            'location_name': 'Location Name',
            'max_participants': 'Maximum Participants',
        }
