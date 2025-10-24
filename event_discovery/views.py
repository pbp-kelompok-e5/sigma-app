from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Event, EventParticipant
from sigma_app.constants import SPORT_CHOICES, CITY_CHOICES
from reviews.models import Review

# Create your views here.

# Show All Event
def show_event(request):
    context={
        'cityChoices' : CITY_CHOICES,
        'sportChoices' : SPORT_CHOICES
    }
    return render(request, 'event_page.html', context)

# Show Event in JSON
def show_json(request):
    event_list = Event.objects.all()
    data=[
        {
            'id' : str(event.id),
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

# JSON By ID
def show_json_by_id(request, id):
    try:
        event = get_object_or_404(Event, pk=id)
        data = {
            'id' : str(event.id),
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
        return JsonResponse(data)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

# Show my Event
def show_my_event(request):
    return render(request, 'event_my.html')

# JSON For Participant
def show_json_my_event(request):
    user = request.user
    # Filter EventParticipant by user
    event_participant = EventParticipant.objects.filter(user=user)
    
    event_list = [participant.event for participant in event_participant]
    data=[
        {
            'id' : str(event.id),
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

# Event Joined
def join_event(request, id):
    event = get_object_or_404(Event, pk=id)


    # Cek Kapasitas Sudah Penuh
    if event.is_full():
        return JsonResponse({'message': 'Event is full'}, status=400)

    # Tambah Participant
    try:
        EventParticipant.objects.create(user=request.user, event=event, status='joined')
        event.current_participants += 1
        event.save()
        return JsonResponse({'message': 'Joined'}, status=201)
    except:
        return JsonResponse({'message': 'Could not join'}, status=400)


# Event Leave
def leave_event(request, id):
    try:
        event = get_object_or_404(Event, pk=id)
        # Cari Partisipan User
        eventparticipant = get_object_or_404(EventParticipant, user=request.user, event=event)
        
        # Hapus Partisipan
        eventparticipant.delete()
        # Kurangi Jumlah Partisipan di Event
        event.current_participants = max(0, event.current_participants - 1)
        event.save() # Update event setelah pengurangan partisipan
        return JsonResponse({'message': 'Left'}, status=201)
    except EventParticipant.DoesNotExist:
        return JsonResponse({'message': 'Not Found'}, status=404)

    
# Event Detail
def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)

    context = {
        'event' : event,
    }
    
    return render(request, 'event_detail.html', context)

# Event Participant Status
def event_participant_status(request, id):
    event = get_object_or_404(Event, pk=id)
    try:
        participant = EventParticipant.objects.get(user=request.user, event=event)
        return JsonResponse({'status': participant.status}, status=200)
    except EventParticipant.DoesNotExist:
        return JsonResponse({'status': 'not_participating'}, status=200)

# Check if event has attended participants (excluding current user)
def event_has_attended_participants(request, id):
    event = get_object_or_404(Event, pk=id)
    # Check if there are any attended participants excluding the current user
    has_attended = EventParticipant.objects.filter(
        event=event,
        status='attended'
    ).exclude(user=request.user).exists()

    return JsonResponse({'has_attended_participants': has_attended}, status=200)

# Check if user has already reviewed participants for this event
def event_user_has_reviewed(request, id):
    event = get_object_or_404(Event, pk=id)
    # Check if the user has submitted any reviews for this event
    has_reviewed = Review.objects.filter(
        event=event,
        from_user=request.user
    ).exists()

    return JsonResponse({'has_reviewed': has_reviewed}, status=200)