# leaderboard/management/commands/fix_total_events.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile
from event_discovery.models import EventParticipant


class Command(BaseCommand):
    help = "Fix total_events count in UserProfile for all users based on their EventParticipant records"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting to fix total_events count..."))
        
        # Get all users
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            try:
                # Get user profile
                profile = UserProfile.objects.get(user=user)
                
                # Count total events (joined or attended, not cancelled)
                total_events = EventParticipant.objects.filter(
                    user=user,
                    status__in=['joined', 'attended']
                ).count()
                
                # Update if different
                if profile.total_events != total_events:
                    old_count = profile.total_events
                    profile.total_events = total_events
                    profile.save()
                    updated_count += 1
                    self.stdout.write(
                        f"Updated {user.username}: {old_count} -> {total_events} events"
                    )
                    
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"UserProfile not found for user: {user.username}")
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f"\nDone! Updated {updated_count} user profiles.")
        )

