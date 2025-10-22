from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Event

# Create your views here.

# Show All Event
def show_event(request):
    event_list = Event.objects.all()
    
    context = {
        'event_list': event_list
    }
    
    return render(request, 'event_page.html')

# Show Event in JSON
def show_json(request):
    event_list = Event.objects.all()
    data=[
        {
            'organizer': event.organizer.username,
            'title': event.title,
            'description': event.description,
            'thumbnail' : event.thumbnail,
            'sport_type': event.sport_type,
            'event_date': event.event_date,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'city': event.city,
            'location_name': event.location_name,
            'max_participants': event.max_participants,
            'current_participants': event.current_participants,
            'status': event.status,
            'created_at': event.created_at,
            'updated_at': event.updated_at,
        }
        for event in event_list
    ]
    return JsonResponse(data, safe=False)

# Show my Event
def show_my_event(request):
    # TODO
    return render(request, 'event_my.html')
