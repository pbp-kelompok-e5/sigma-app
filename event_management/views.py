from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from event_discovery.models import Event, EventParticipant
from .forms import EventForm
from datetime import date

from django.http import JsonResponse
from django.urls import reverse
import json


# ========== INTERNAL HELPERS ==========

def _is_ajax(request):
    """Check if the request came from JS fetch() / AJAX."""
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _get_request_data(request):
    """
    Handle both form-encoded and JSON AJAX submissions.
    Returns a dictionary suitable for passing to Django forms.
    """
    # For normal POST forms
    if request.method == "POST" and request.POST:
        return request.POST

    # For JSON AJAX submissions
    try:
        if request.body:
            body_data = json.loads(request.body.decode("utf-8"))
            if isinstance(body_data, dict):
                return body_data
    except json.JSONDecodeError:
        pass

    return {}


# ========== VIEWS ==========

@login_required
def create_event(request):
    if request.method == 'POST':
        data = _get_request_data(request)
        form = EventForm(data)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            if _is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('event_management:my_events'),
                    'message': 'Event created successfully!'
                })
            messages.success(request, 'Event created successfully!')
            return redirect('event_management:my_events')

        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

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
        data = _get_request_data(request)
        form = EventForm(data, instance=event)

        if form.is_valid():
            form.save()
            if _is_ajax(request):
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('event_management:my_events'),
                    'message': 'Event updated successfully!'
                })
            messages.success(request, 'Event updated successfully!')
            return redirect('event_management:my_events')

        else:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = EventForm(instance=event)

    return render(request, 'event_management/update_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == 'POST' or request.method == 'DELETE':
        event.delete()
        if _is_ajax(request):
            return JsonResponse({'success': True, 'event_id': event_id, 'message': 'Event deleted successfully!'})
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_management:my_events')

    return redirect('event_management:my_events')


@login_required
def cancel_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == 'POST' or request.method == 'PATCH':
        event.status = 'cancelled'
        event.save()
        if _is_ajax(request):
            return JsonResponse({'success': True, 'event_id': event_id, 'message': 'Event cancelled successfully!'})
        messages.info(request, 'Event has been cancelled.')
        return redirect('event_management:my_events')

    return redirect('event_management:my_events')


@login_required
def manage_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    participants = EventParticipant.objects.filter(event=event)

    if request.method == 'POST':
        data = _get_request_data(request)
        action = data.get('action')
        user_id = data.get('user_id')

        if not action or not user_id:
            if _is_ajax(request):
                return JsonResponse({'success': False, 'message': 'Missing parameters.'}, status=400)
            messages.error(request, 'Missing parameters.')
            return redirect('event_management:manage_participants', event_id=event.id)

        if action == 'remove':
            deleted, _ = EventParticipant.objects.filter(event=event, user_id=user_id).delete()
            if _is_ajax(request):
                return JsonResponse({
                    'success': True if deleted else False,
                    'action': 'remove',
                    'user_id': int(user_id),
                    'message': 'Participant removed.' if deleted else 'Participant not found.'
                }, status=200 if deleted else 404)
            messages.warning(request, 'Participant removed.' if deleted else 'Participant not found.')
            return redirect('event_management:manage_participants', event_id=event.id)

        elif action == 'mark_attended':
            participant = EventParticipant.objects.filter(event=event, user_id=user_id).first()
            if participant:
                participant.status = 'attended'
                participant.save()
                if _is_ajax(request):
                    return JsonResponse({
                        'success': True,
                        'action': 'mark_attended',
                        'user_id': int(user_id),
                        'message': 'Attendance marked.'
                    })
                messages.success(request, 'Attendance marked.')
            else:
                if _is_ajax(request):
                    return JsonResponse({'success': False, 'message': 'Participant not found.'}, status=404)
                messages.error(request, 'Participant not found.')

            return redirect('event_management:manage_participants', event_id=event.id)

    return render(request, 'event_management/manage_participants.html', {
        'event': event,
        'participants': participants
    })
