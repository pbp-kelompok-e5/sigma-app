from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from event_discovery.models import Event, EventParticipant
from .forms import EventForm
from datetime import date

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_management:my_events')
    else:
        form = EventForm()
    return render(request, 'event_management/create_event.html', {'form': form})

@login_required
def my_events(request):
    events = Event.objects.filter(organizer=request.user).order_by('-event_date')
    today = date.today()
    context = {
        'upcoming_events': events.filter(event_date__gte=today),
        'past_events': events.filter(event_date__lt=today)
    }
    return render(request, 'event_management/my_events.html', context)

@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_management:my_events')
    else:
        form = EventForm(instance=event)
    return render(request, 'event_management/update_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('event_management:my_events')

@login_required
def cancel_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.status = 'cancelled'
    event.save()
    messages.info(request, 'Event has been cancelled.')
    return redirect('event_management:my_events')

@login_required
def manage_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    participants = EventParticipant.objects.filter(event=event)

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'remove':
            EventParticipant.objects.filter(event=event, user_id=user_id).delete()
            messages.warning(request, 'Participant removed.')
        elif action == 'mark_attended':
            participant = EventParticipant.objects.filter(event=event, user_id=user_id).first()
            if participant:
                participant.status = 'attended'
                participant.save()
                messages.success(request, 'Attendance marked.')

        return redirect('event_management:manage_participants', event_id=event.id)

    return render(request, 'event_management/manage_participants.html', {
        'event': event,
        'participants': participants
    })