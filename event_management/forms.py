from django import forms
from event_discovery.models import Event

class EventForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'sport_type', 'thumbnail', 'event_date',
            'start_time', 'end_time', 'city', 'location_name',
            'max_participants',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
