"""
Event Management module

Note:
This module does not define its own models.
It reuses Event and EventParticipant from event_discovery.models
to ensure shared database tables and consistent event data.
"""

from django.db import models
from event_discovery.models import Event, EventParticipant