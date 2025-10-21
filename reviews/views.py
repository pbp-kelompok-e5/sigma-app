from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Review, UserRating
from event_discovery.models import Event, EventParticipant
from django.db.models import Avg, Count

@login_required
def event_reviews(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reviews = Review.objects.filter(event=event)

    # Ambil peserta attended (kecuali diri sendiri)
    participants = User.objects.filter(
        joined_events__event=event,
        joined_events__status='attended'
    ).exclude(id=request.user.id)

    # Submit Multiple Reviews
    if request.method == 'POST':
        from_user = request.user
        created_any = False

        for to_user in participants:
            rating = request.POST.get(f"rating_{to_user.id}")
            comment = request.POST.get(f"comment_{to_user.id}")

            # Skip jika kosong
            if not rating or not comment:
                continue

            # Cegah double review
            if Review.objects.filter(event=event, from_user=from_user, to_user=to_user).exists():
                continue

            Review.objects.create(
                event=event,
                from_user=from_user,
                to_user=to_user,
                rating=rating,
                comment=comment
            )

            update_user_rating(to_user)
            created_any = True

        if created_any:
            messages.success(request, "All reviews submitted successfully!")
        else:
            messages.warning(request, "No reviews were submitted.")

        return redirect('reviews:event-reviews', event_id=event.id)

    return render(request, 'reviews/event_reviews.html', {
        'event': event,
        'reviews': reviews,
        'participants': participants
    })


def update_user_rating(user):
    reviews = Review.objects.filter(to_user=user)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    star_count = reviews.values('rating').annotate(count=Count('rating'))

    user_rating, created = UserRating.objects.get_or_create(user=user)
    user_rating.average_rating = avg_rating
    user_rating.total_reviews = reviews.count()

    user_rating.one_star = user_rating.two_star = user_rating.three_star = user_rating.four_star = user_rating.five_star = 0
    for item in star_count:
        rating = item['rating']
        count = item['count']
        if rating == 1: user_rating.one_star = count
        if rating == 2: user_rating.two_star = count
        if rating == 3: user_rating.three_star = count
        if rating == 4: user_rating.four_star = count
        if rating == 5: user_rating.five_star = count

    user_rating.save()
