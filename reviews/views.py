from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Review, UserRating
from event_discovery.models import Event, EventParticipant
from django.db.models import Avg, Count
from authentication.models import UserProfile
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

@login_required
def event_reviews(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reviews = Review.objects.filter(event=event)

    # Ambil peserta attended (kecuali diri sendiri)
    participants = User.objects.filter(
    joined_events__event=event,
    joined_events__status='attended'
).exclude(id=request.user.id).select_related('profile')

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
            comment=comment or "No comment"
        )

            update_user_rating(to_user)
            created_any = True

        if created_any:
            messages.success(request, "All reviews submitted successfully!")
        else:
            messages.warning(request, "No reviews were submitted. Please rate at least one participant.")


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

@login_required
def user_reviews(request, user_id):
    user = get_object_or_404(User, id=user_id)
    reviews = Review.objects.filter(to_user=user).select_related('from_user').order_by('-created_at')

    return render(request, 'reviews/user_reviews.html', {
        'reviewed_user': user,
        'reviews': reviews
    })

@login_required
def user_written_reviews(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # hanya user yg sama boleh akses halaman ini
    if request.user != user:
        messages.error(request, "You are not allowed to view this page.")
        return redirect('/')

    reviews = Review.objects.filter(from_user=user).select_related('to_user', 'event').order_by('-created_at')
    return render(request, 'reviews/user_written_reviews.html', {
        'writer': user,
        'reviews': reviews
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # hanya penulisnya yg boleh edit
    if review.from_user != request.user:
        messages.error(request, "You cannot edit someone else's review.")
        return redirect('/')

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "No comment")

        review.rating = rating
        review.comment = comment
        review.save()

        update_user_rating(review.to_user)
        messages.success(request, "Review updated successfully!")
        return redirect('reviews:user-written-reviews', user_id=request.user.id)

    return render(request, 'reviews/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.from_user != request.user:
        messages.error(request, "You cannot delete this review.")
        return redirect('/')

    to_user = review.to_user
    review.delete()
    update_user_rating(to_user)

    messages.success(request, "Review deleted.")
    return redirect('reviews:user-written-reviews', user_id=request.user.id)

@login_required
@require_POST
def ajax_update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.from_user != request.user:
        return JsonResponse({'ok': False, 'error': "Forbidden"}, status=403)

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', 'No comment')

    if not rating:
        return JsonResponse({'ok': False, 'error': "Rating is required"}, status=400)

    try:
        rating_int = int(rating)
        if not (1 <= rating_int <= 5):
            raise ValueError()
    except ValueError:
        return JsonResponse({'ok': False, 'error': "Rating must be 1-5"}, status=400)

    review.rating = rating_int
    review.comment = comment or "No comment"
    review.save()
    update_user_rating(review.to_user)

    return JsonResponse({
        'ok': True,
        'review': {
            'id': review.id,
            'to_user': review.to_user.username,
            'event_title': review.event.title,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
@require_POST
def ajax_delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.from_user != request.user:
        return JsonResponse({'ok': False, 'error': "Forbidden"}, status=403)

    to_user = review.to_user
    review_id_copy = review.id
    review.delete()
    update_user_rating(to_user)

    return JsonResponse({'ok': True, 'deleted_id': review_id_copy})


@login_required
@require_POST
def ajax_create_event_reviews(request, event_id):
    """
    Terima form dari event_reviews (rating_{user_id}, comment_{user_id})
    Buat banyak review sekaligus (skip yang kosong), return ringkasan JSON.
    """
    event = get_object_or_404(Event, id=event_id)
    from_user = request.user

    # Peserta attended (kecuali diri sendiri)
    participants = User.objects.filter(
        joined_events__event=event,
        joined_events__status='attended'
    ).exclude(id=from_user.id)

    created = []
    skipped = []

    for to_user in participants:
        rating = request.POST.get(f'rating_{to_user.id}')
        comment = request.POST.get(f'comment_{to_user.id}', 'No comment')

        if not rating:
            skipped.append(to_user.id)
            continue

        if Review.objects.filter(event=event, from_user=from_user, to_user=to_user).exists():
            skipped.append(to_user.id)
            continue

        try:
            rating_int = int(rating)
            if not (1 <= rating_int <= 5):
                raise ValueError()
        except ValueError:
            skipped.append(to_user.id)
            continue

        review = Review.objects.create(
            event=event,
            from_user=from_user,
            to_user=to_user,
            rating=rating_int,
            comment=comment or "No comment"
        )
        update_user_rating(to_user)
        created.append({
            'id': review.id,
            'to_user': to_user.username,
            'rating': review.rating,
            'comment': review.comment,
            'event_title': event.title,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({'ok': True, 'created': created, 'skipped': skipped})

