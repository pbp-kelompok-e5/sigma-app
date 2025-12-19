"""
Signals untuk Leaderboard Module
Berisi signal handlers untuk automatic point tracking dari berbagai aktivitas.
Signals ini akan dipanggil otomatis ketika ada perubahan di model lain (Event, Review, dll).
"""

# Import signal types dan receiver decorator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Import timezone untuk handling waktu
from django.utils import timezone
from datetime import timedelta

# Import model-model yang akan di-listen
from event_discovery.models import EventParticipant, Event
from reviews.models import Review
# Import model-model leaderboard
from leaderboard.models import PointTransaction, Achievement


# ===== POINT TRANSACTION CONSTANTS =====
# Konfigurasi jumlah poin untuk setiap jenis aktivitas
# Bisa diubah di sini untuk adjust point system
POINTS_CONFIG = {
    'event_join': 10,           # Poin saat user join event
    'event_complete': 30,       # Poin saat user hadir di event
    'event_organize': 50,       # Poin saat organizer menyelesaikan event
    'review_given': 5,          # Poin saat user memberi review
    'five_star_received': 10,   # Poin saat user menerima review bintang 5
}


# ===== EVENT PARTICIPANT SIGNALS =====

@receiver(post_save, sender=EventParticipant)
def award_points_on_event_join(sender, instance, created, **kwargs):
    """
    Signal handler untuk memberikan poin ketika user bergabung dengan event.
    Dipanggil otomatis setiap kali EventParticipant dibuat atau diupdate.

    Args:
        sender: Model class yang mengirim signal (EventParticipant)
        instance: Instance EventParticipant yang baru dibuat/diupdate
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True)
    2. Cek apakah status participant adalah 'joined'
    3. Jika ya, buat PointTransaction dengan poin event_join
    """
    # Hanya proses jika ini record baru DAN status adalah 'joined'
    if created and instance.status == 'joined':
        # Buat transaksi poin baru
        PointTransaction.objects.create(
            user=instance.user,
            activity_type='event_join',
            points=POINTS_CONFIG['event_join'],
            description=f"Joined event: {instance.event.title}",
            related_event=instance.event
        )


@receiver(post_save, sender=EventParticipant)
def update_total_events_on_join(sender, instance, created, **kwargs):
    """
    Signal handler untuk update total_events di UserProfile ketika user join event.
    Dipanggil otomatis setiap kali EventParticipant dibuat.

    Args:
        sender: Model class yang mengirim signal (EventParticipant)
        instance: Instance EventParticipant yang baru dibuat
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True)
    2. Ambil UserProfile dari user yang terkait
    3. Hitung total event yang diikuti user (status 'joined' atau 'attended')
    4. Update field total_events di UserProfile
    5. Save UserProfile
    """
    # Hanya proses jika ini record baru
    if created:
        # Import UserProfile di dalam fungsi untuk menghindari circular import
        from authentication.models import UserProfile

        try:
            # Ambil UserProfile dari user yang terkait
            profile = UserProfile.objects.get(user=instance.user)

            # Hitung total event yang diikuti user (status 'joined' atau 'attended')
            # Tidak termasuk yang 'cancelled'
            total_events = EventParticipant.objects.filter(
                user=instance.user,
                status__in=['joined', 'attended']
            ).count()

            # Update total_events di UserProfile
            profile.total_events = total_events

            # Simpan perubahan ke database
            profile.save()

        except UserProfile.DoesNotExist:
            # Jika UserProfile belum ada, skip (tidak perlu error)
            pass


@receiver(post_save, sender=EventParticipant)
def award_points_on_event_complete(sender, instance, created, **kwargs):
    """
    Signal handler untuk memberikan poin ketika user menyelesaikan event (hadir).
    Dipanggil otomatis setiap kali EventParticipant diupdate.

    Args:
        sender: Model class yang mengirim signal (EventParticipant)
        instance: Instance EventParticipant yang diupdate
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini update (created=False) DAN status berubah jadi 'attended'
    2. Cek apakah sudah ada transaksi poin untuk event ini (prevent duplicate)
    3. Jika belum ada, buat PointTransaction dengan poin event_complete
    """
    # Hanya proses jika ini update (bukan record baru) DAN status adalah 'attended'
    # not created: Ini adalah update, bukan insert baru
    if not created and instance.status == 'attended':
        # Cek apakah sudah ada transaksi poin untuk event ini
        # Ini untuk mencegah duplikat poin jika status diupdate berkali-kali
        existing = PointTransaction.objects.filter(
            user=instance.user,
            activity_type='event_complete',
            related_event=instance.event
        ).exists()

        # Jika belum ada transaksi, buat transaksi poin baru
        if not existing:
            PointTransaction.objects.create(
                user=instance.user,
                activity_type='event_complete',
                points=POINTS_CONFIG['event_complete'],
                description=f"Completed event: {instance.event.title}",
                related_event=instance.event
            )


@receiver(post_save, sender=EventParticipant)
def update_total_events_on_status_change(sender, instance, created, **kwargs):
    """
    Signal handler untuk update total_events di UserProfile ketika status EventParticipant berubah.
    Dipanggil otomatis setiap kali EventParticipant diupdate.

    Args:
        sender: Model class yang mengirim signal (EventParticipant)
        instance: Instance EventParticipant yang diupdate
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini update (created=False)
    2. Ambil UserProfile dari user yang terkait
    3. Hitung total event yang diikuti user (status 'joined' atau 'attended')
    4. Update field total_events di UserProfile
    5. Save UserProfile
    """
    # Hanya proses jika ini update (bukan record baru)
    if not created:
        # Import UserProfile di dalam fungsi untuk menghindari circular import
        from authentication.models import UserProfile

        try:
            # Ambil UserProfile dari user yang terkait
            profile = UserProfile.objects.get(user=instance.user)

            # Hitung total event yang diikuti user (status 'joined' atau 'attended')
            # Tidak termasuk yang 'cancelled'
            total_events = EventParticipant.objects.filter(
                user=instance.user,
                status__in=['joined', 'attended']
            ).count()

            # Update total_events di UserProfile
            profile.total_events = total_events

            # Simpan perubahan ke database
            profile.save()

        except UserProfile.DoesNotExist:
            # Jika UserProfile belum ada, skip (tidak perlu error)
            pass


@receiver(post_delete, sender=EventParticipant)
def update_total_events_on_delete(sender, instance, **kwargs):
    """
    Signal handler untuk update total_events di UserProfile ketika EventParticipant dihapus.
    Dipanggil otomatis setiap kali EventParticipant dihapus (misalnya user leave event).

    Args:
        sender: Model class yang mengirim signal (EventParticipant)
        instance: Instance EventParticipant yang dihapus
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Ambil UserProfile dari user yang terkait
    2. Hitung total event yang diikuti user (status 'joined' atau 'attended')
    3. Update field total_events di UserProfile
    4. Save UserProfile
    """
    # Import UserProfile di dalam fungsi untuk menghindari circular import
    from authentication.models import UserProfile

    try:
        # Ambil UserProfile dari user yang terkait
        profile = UserProfile.objects.get(user=instance.user)

        # Hitung total event yang diikuti user (status 'joined' atau 'attended')
        # Tidak termasuk yang 'cancelled'
        total_events = EventParticipant.objects.filter(
            user=instance.user,
            status__in=['joined', 'attended']
        ).count()

        # Update total_events di UserProfile
        profile.total_events = total_events

        # Simpan perubahan ke database
        profile.save()

    except UserProfile.DoesNotExist:
        # Jika UserProfile belum ada, skip (tidak perlu error)
        pass


# ===== EVENT SIGNALS =====

@receiver(post_save, sender=Event)
def award_points_on_event_organize(sender, instance, created, **kwargs):
    """
    Signal handler untuk memberikan poin ketika organizer menyelesaikan event.
    Dipanggil otomatis setiap kali Event diupdate.

    Args:
        sender: Model class yang mengirim signal (Event)
        instance: Instance Event yang diupdate
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini update (created=False) DAN status berubah jadi 'completed'
    2. Cek apakah sudah ada transaksi poin untuk event ini (prevent duplicate)
    3. Jika belum ada, buat PointTransaction dengan poin event_organize
    """
    # Hanya proses jika ini update (bukan record baru) DAN status adalah 'completed'
    if not created and instance.status == 'completed':
        # Cek apakah sudah ada transaksi poin untuk event ini
        # Ini untuk mencegah duplikat poin jika status diupdate berkali-kali
        existing = PointTransaction.objects.filter(
            user=instance.organizer,
            activity_type='event_organize',
            related_event=instance
        ).exists()

        # Jika belum ada transaksi, buat transaksi poin baru
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
    """
    Signal handler untuk memberikan poin ketika user memberi review.
    Dipanggil otomatis setiap kali Review dibuat.

    Args:
        sender: Model class yang mengirim signal (Review)
        instance: Instance Review yang baru dibuat
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True)
    2. Buat PointTransaction untuk user yang memberi review (from_user)
    """
    # Hanya proses jika ini record baru
    if created:
        # Buat transaksi poin untuk user yang memberi review
        PointTransaction.objects.create(
            user=instance.from_user,
            activity_type='review_given',
            points=POINTS_CONFIG['review_given'],
            description=f"Gave review to {instance.to_user.username}",
            related_event=instance.event
        )


@receiver(post_save, sender=Review)
def award_points_on_five_star_review(sender, instance, created, **kwargs):
    """
    Signal handler untuk memberikan poin ketika user menerima review bintang 5.
    Dipanggil otomatis setiap kali Review dibuat.

    Args:
        sender: Model class yang mengirim signal (Review)
        instance: Instance Review yang baru dibuat
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True) DAN rating adalah 5
    2. Buat PointTransaction untuk user yang menerima review (to_user)
    """
    # Hanya proses jika ini record baru DAN rating adalah 5
    if created and instance.rating == 5:
        # Buat transaksi poin untuk user yang menerima review bintang 5
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
    """
    Signal handler untuk mengecek dan memberikan achievement berdasarkan aktivitas user.
    Dipanggil otomatis setiap kali PointTransaction dibuat.

    Achievement yang dicek:
    1. First Event: Join event pertama kali
    2. 10 Events: Menyelesaikan 10 event
    3. Organizer: Menyelenggarakan 5 event
    4. Highly Rated: Menerima 10 review bintang 5

    Args:
        sender: Model class yang mengirim signal (PointTransaction)
        instance: Instance PointTransaction yang baru dibuat
        created: Boolean, True jika ini record baru (bukan update)
        **kwargs: Keyword arguments tambahan dari signal

    Flow:
    1. Cek apakah ini record baru (created=True)
    2. Untuk setiap jenis achievement, cek apakah user memenuhi syarat
    3. Jika memenuhi syarat DAN belum punya achievement, buat Achievement baru
    4. Berikan bonus poin via PointTransaction baru
    """
    # Hanya proses jika ini record baru
    if not created:
        return

    # Ambil user dari transaksi poin
    user = instance.user

    # ===== FIRST EVENT ACHIEVEMENT =====
    # Syarat: User join event pertama kali
    # Bonus: 5 poin
    if instance.activity_type == 'event_join':
        # Cek apakah user sudah punya achievement 'first_event'
        if not Achievement.objects.filter(user=user, achievement_code='first_event').exists():
            # Buat achievement baru
            Achievement.objects.create(
                user=user,
                achievement_code='first_event',
                title='🏃 First Event',
                description='Joined your first event',
                bonus_points=5
            )
            # Berikan bonus poin
            # Ini akan trigger signal ini lagi, tapi tidak akan infinite loop
            # karena activity_type bukan 'event_join'
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=5,
                description='Achievement bonus: First Event'
            )

    # ===== 10 EVENTS ACHIEVEMENT =====
    # Syarat: User menyelesaikan 10 event
    # Bonus: 20 poin
    # Hitung jumlah event yang sudah diselesaikan user
    completed_events = PointTransaction.objects.filter(
        user=user,
        activity_type='event_complete'
    ).count()

    # Jika sudah 10 event atau lebih
    if completed_events >= 10:
        # Cek apakah user sudah punya achievement 'ten_events'
        if not Achievement.objects.filter(user=user, achievement_code='ten_events').exists():
            # Buat achievement baru
            Achievement.objects.create(
                user=user,
                achievement_code='ten_events',
                title='🎯 10 Events',
                description='Completed 10 events',
                bonus_points=20
            )
            # Berikan bonus poin
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=20,
                description='Achievement bonus: 10 Events'
            )

    # ===== ORGANIZER ACHIEVEMENT =====
    # Syarat: User menyelenggarakan 5 event yang sudah completed
    # Bonus: 30 poin
    # Hitung jumlah event yang diselenggarakan user dengan status 'completed'
    organized_events = Event.objects.filter(
        organizer=user,
        status='completed'
    ).count()

    # Jika sudah 5 event atau lebih
    if organized_events >= 5:
        # Cek apakah user sudah punya achievement 'organizer'
        if not Achievement.objects.filter(user=user, achievement_code='organizer').exists():
            # Buat achievement baru
            Achievement.objects.create(
                user=user,
                achievement_code='organizer',
                title='👑 Organizer',
                description='Organized 5 events',
                bonus_points=30
            )
            # Berikan bonus poin
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=30,
                description='Achievement bonus: Organizer'
            )

    # ===== HIGHLY RATED ACHIEVEMENT =====
    # Syarat: User menerima 10 review bintang 5
    # Bonus: 25 poin
    # Hitung jumlah review bintang 5 yang diterima user
    five_star_count = PointTransaction.objects.filter(
        user=user,
        activity_type='five_star_received'
    ).count()

    # Jika sudah 10 review bintang 5 atau lebih
    if five_star_count >= 10:
        # Cek apakah user sudah punya achievement 'highly_rated'
        if not Achievement.objects.filter(user=user, achievement_code='highly_rated').exists():
            # Buat achievement baru
            Achievement.objects.create(
                user=user,
                achievement_code='highly_rated',
                title='⭐ Highly Rated',
                description='Received 10 five-star reviews',
                bonus_points=25
            )
            # Berikan bonus poin
            PointTransaction.objects.create(
                user=user,
                activity_type='event_join',
                points=25,
                description='Achievement bonus: Highly Rated'
            )

