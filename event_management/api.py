# event_management/api.py
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .forms import EventForm
from event_discovery.models import Event, EventParticipant
import json
from django.core.exceptions import ValidationError

def _json_body(request):
    try:
        if request.body:
            return json.loads(request.body.decode("utf-8"))
    except Exception:
        pass
    return {}

# List organizer events (requires login)
@login_required
def api_my_events(request):
    user = request.user
    events = Event.objects.filter(organizer=user).order_by('-event_date', '-start_time')
    data = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "thumbnail": e.thumbnail or "",
            "sport_type": e.sport_type,
            "event_date": e.event_date.isoformat(),
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "city": e.city,
            "location_name": e.location_name,
            "max_participants": e.max_participants,
            "current_participants": e.current_participants,
            "status": e.status,
            "created_at": e.created_at.isoformat(),
            "updated_at": e.updated_at.isoformat(),
        } for e in events
    ]
    return JsonResponse(data, safe=False)

# Detail (organizer can see it via same endpoint; read-only even if not organizer)
@login_required
def api_event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    data = {
        "id": event.id,
        "organizer": event.organizer.username,
        "title": event.title,
        "description": event.description,
        "thumbnail": event.thumbnail or "",
        "sport_type": event.sport_type,
        "event_date": event.event_date.isoformat(),
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "city": event.city,
        "location_name": event.location_name,
        "max_participants": event.max_participants,
        "current_participants": event.current_participants,
        "status": event.status,
        "created_at": event.created_at.isoformat(),
        "updated_at": event.updated_at.isoformat(),
    }
    return JsonResponse(data)

# Create event (organizer) — reuse EventForm for validation
@csrf_exempt
@login_required
def api_create_event(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    body = _json_body(request)
    # populate form using EventForm; EventForm expects normal dict
    form = EventForm(body)
    if form.is_valid():
        event = form.save(commit=False)
        event.organizer = request.user
        event.save()
        return JsonResponse({"success": True, "id": event.id, "message": "Event created"}, status=201)
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

# Update event (organizer only)
@csrf_exempt
@login_required
def api_update_event(request, event_id):
    if request.method not in ("POST", "PUT", "PATCH"):
        return HttpResponseBadRequest("Only POST/PUT/PATCH allowed")
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)
    body = _json_body(request)
    form = EventForm(body, instance=event)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True, "message": "Event updated"})
    else:
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

# Delete event (organizer only)
@csrf_exempt
@login_required
def api_delete_event(request, event_id):
    if request.method not in ("POST", "DELETE"):
        return HttpResponseBadRequest("Only POST/DELETE allowed")
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)
    try:
        event.delete()
        return JsonResponse({"success": True, "message": "Event deleted"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

# Participants list (organizer only)
@login_required
def api_participants_list(request, event_id):
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)
    parts = EventParticipant.objects.filter(event=event)
    data = [
        {
            "user_id": p.user.id,
            "username": p.user.username,
            "status": p.status,
            "joined_at": p.joined_at.isoformat(),
        } for p in parts
    ]
    return JsonResponse(data, safe=False)

# Manage participant: remove / mark_attended (organizer only)
@csrf_exempt
@login_required
def api_manage_participant(request, event_id):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    event = get_object_or_404(Event, pk=event_id, organizer=request.user)
    body = _json_body(request)
    action = body.get("action")
    user_id = body.get("user_id")
    if not action or user_id is None:
        return JsonResponse({"success": False, "message": "Missing parameters"}, status=400)
    try:
        if action == "remove":
            deleted, _ = EventParticipant.objects.filter(event=event, user_id=user_id).delete()
            if deleted:
                event.current_participants = max(0, event.current_participants - 1)
                event.save()
                return JsonResponse({"success": True, "message": "Participant removed"})
            return JsonResponse({"success": False, "message": "Participant not found"}, status=404)
        elif action == "mark_attended":
            p = EventParticipant.objects.filter(event=event, user_id=user_id).first()
            if not p:
                return JsonResponse({"success": False, "message": "Participant not found"}, status=404)
            p.status = "attended"
            p.save()
            return JsonResponse({"success": True, "message": "Marked attended"})
        else:
            return JsonResponse({"success": False, "message": "Unknown action"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
