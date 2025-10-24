"""
Signals untuk automatic point tracking dari berbagai aktivitas
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from event_discovery.models import EventParticipant, Event
from reviews.models import Review
from leaderboard.models import PointTransaction, Achievement


# ===== POINT TRANSACTION CONSTANTS =====
POINTS_CONFIG = {
    'event_join': 10,
    'event_complete': 30,
    'event_organize': 50,
    'review_given': 5,
    'five_star_received': 10,
}


# ===== EVENT PARTICIPANT SIGNALS =====
@receiver(post_save, sender=EventParticipant)
def award_points_on_event_join(sender, instance, created, **kwargs):
    """Award points ketika user bergabung dengan event"""
    if created and instance.status == 'joined':
        PointTransaction.objects.create(
            user=instance.user,
            activity_type='event_join',
            points=POINTS_CONFIG['event_join'],
            description=f"Joined event: {instance.event.title}",
            related_event=instance.event
        )


@receiver(post_save, sender=EventParticipant)
def award_points_on_event_complete(sender, instance, created, **kwargs):
    """Award points ketika user hadir di event (status = attended)"""
    if not created and instance.status == 'attended':
        # Cek apakah sudah ada transaksi untuk event ini
        existing = PointTransaction.objects.filter(
            user=instance.user,
            activity_type='event_complete',
            related_event=instance.event
        ).exists()
        
        if not existing:
            PointTransaction.objects.create(
                user=instance.user,
                activity_type='event_complete',
                points=POINTS_CONFIG['event_complete'],
                description=f"Completed event: {instance.event.title}",
                related_event=instance.event
            )


# ===== EVENT SIGNALS =====
@receiver(post_save, sender=Event)
def award_points_on_event_organize(sender, instance, created, **kwargs):
    """Award points ketika event organizer menyelesaikan event"""
    if not created and instance.status == 'completed':
        # Cek apakah sudah ada transaksi untuk event ini
        existing = PointTransaction.objects.filter(
            user=instance.organizer,
            activity_type='event_organize',
            related_event=instance
        ).exists()
        
        if not existing:
            PointTransaction.objects.create(
                user=instance.organizer,
                activity_type='event_organize',
                points=POINTS_CONFIG['event_organize'],
                description=f"Organized event: {instance.title}",
                related_event=instance
            )


# ===== REVIEW SIGNALS =====
@receiver(post_save, sender=Review)
def award_points_on_review_given(sender, instance, created, **kwargs):
    """Award points ketika user memberikan review"""
    if created:
        PointTransaction.objects.create(
            user=instance.from_user,
            activity_type='review_given',
            points=POINTS_CONFIG['review_given'],
            description=f"Gave review to {instance.to_user.username}",
            related_event=instance.event
        )


@receiver(post_save, sender=Review)
def award_points_on_five_star_review(sender, instance, created, **kwargs):
    """Award points ketika user menerima review bintang 5"""
    if created and instance.rating == 5:
        PointTransaction.objects.create(
            user=instance.to_user,
            activity_type='five_star_received',
            points=POINTS_CONFIG['five_star_received'],
            description=f"Received 5-star review from {instance.from_user.username}",
            related_event=instance.event
        )


# ===== ACHIEVEMENT SIGNALS =====
@receiver(post_save, sender=PointTransaction)
def check_achievements(sender, instance, created, **kwargs):
    """Check dan award achievements berdasarkan aktivitas user"""
    if not created:
        return
    
    user = instance.user
    
    # First Event Achievement
    if instance.activity_type == 'event_join':
        if not Achievement.objects.filter(user=user, achievement_code='first_event').exists():
            Achievement.objects.create(
                user=user,
                achievement_code='first_event',
                title='🏃 First Event',
                description='Joined your first event',
                bonus_points=5
            )
            # Award bonus points
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=5,
                description='Achievement bonus: First Event'
            )
    
    # 10 Events Achievement
    completed_events = PointTransaction.objects.filter(
        user=user,
        activity_type='event_complete'
    ).count()
    
    if completed_events >= 10:
        if not Achievement.objects.filter(user=user, achievement_code='ten_events').exists():
            Achievement.objects.create(
                user=user,
                achievement_code='ten_events',
                title='🎯 10 Events',
                description='Completed 10 events',
                bonus_points=20
            )
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=20,
                description='Achievement bonus: 10 Events'
            )
    
    # Organizer Achievement
    organized_events = Event.objects.filter(
        organizer=user,
        status='completed'
    ).count()
    
    if organized_events >= 5:
        if not Achievement.objects.filter(user=user, achievement_code='organizer').exists():
            Achievement.objects.create(
                user=user,
                achievement_code='organizer',
                title='👑 Organizer',
                description='Organized 5 events',
                bonus_points=30
            )
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=30,
                description='Achievement bonus: Organizer'
            )
    
    # Highly Rated Achievement
    five_star_count = PointTransaction.objects.filter(
        user=user,
        activity_type='five_star_received'
    ).count()
    
    if five_star_count >= 10:
        if not Achievement.objects.filter(user=user, achievement_code='highly_rated').exists():
            Achievement.objects.create(
                user=user,
                achievement_code='highly_rated',
                title='⭐ Highly Rated',
                description='Received 10 five-star reviews',
                bonus_points=25
            )
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=25,
                description='Achievement bonus: Highly Rated'
            )

