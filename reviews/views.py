from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Review, UserRating
from event_discovery.models import Event
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- Helper Function ---
def update_user_rating(user):
    """
    Menghitung ulang rating rata-rata dan distribusi bintang user.
    """
    reviews = Review.objects.filter(to_user=user)
    
    # Hitung rata-rata
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Hitung jumlah per bintang
    # Menghasilkan output seperti: [{'rating': 5, 'count': 2}, {'rating': 4, 'count': 1}]
    star_counts = reviews.values('rating').annotate(count=Count('rating'))
    
    # Konversi ke dictionary untuk akses cepat: {5: 2, 4: 1}
    star_map = {item['rating']: item['count'] for item in star_counts}

    user_rating, created = UserRating.objects.get_or_create(user=user)
    user_rating.average_rating = avg_rating
    user_rating.total_reviews = reviews.count()

    # Set jumlah bintang
    user_rating.one_star = star_map.get(1, 0)
    user_rating.two_star = star_map.get(2, 0)
    user_rating.three_star = star_map.get(3, 0)
    user_rating.four_star = star_map.get(4, 0)
    user_rating.five_star = star_map.get(5, 0)

    user_rating.save()

# --- Views ---

@login_required
def event_reviews(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    reviews = Review.objects.filter(event=event)

    # Ambil peserta attended (kecuali diri sendiri)
    participants = User.objects.filter(
        joined_events__event=event,
        joined_events__status='attended'
    ).exclude(id=request.user.id).select_related('profile')

    if request.method == 'POST':
        from_user = request.user
        created_any = False

        # OPTIMASI: Ambil semua ID user yang SUDAH direview oleh user ini di event ini
        # untuk menghindari query DB di dalam loop (N+1 Problem)
        existing_review_targets = set(
            Review.objects.filter(event=event, from_user=from_user)
            .values_list('to_user_id', flat=True)
        )

        for to_user in participants:
            # Skip jika user ini sudah pernah direview
            if to_user.id in existing_review_targets:
                continue

            rating = request.POST.get(f"rating_{to_user.id}")
            comment = request.POST.get(f"comment_{to_user.id}")

            # Skip jika form kosong
            if not rating:
                continue

            # Validasi Rating
            try:
                rating_int = int(rating)
                if not (1 <= rating_int <= 5): continue
            except ValueError:
                continue

            Review.objects.create(
                event=event,
                from_user=from_user,
                to_user=to_user,
                rating=rating_int,
                comment=comment or "No comment"
            )
            update_user_rating(to_user)
            created_any = True

        if created_any:
            messages.success(request, "All reviews submitted successfully!")
        else:
            messages.warning(request, "No new reviews were submitted.")

        return redirect('reviews:event-reviews', event_id=event.id)

    return render(request, 'reviews/event_reviews.html', {
        'event': event,
        'reviews': reviews,
        'participants': participants
    })


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
    reviews = Review.objects.filter(from_user=user).select_related('to_user', 'event').order_by('-created_at')
    
    return render(request, 'reviews/user_written_reviews.html', {
        'writer': user,
        'reviews': reviews
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Validasi kepemilikan
    if review.from_user != request.user:
        messages.error(request, "You cannot edit someone else's review.")
        return redirect('/')

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "No comment")

        # Validasi sederhana
        if rating and rating.isdigit() and 1 <= int(rating) <= 5:
            review.rating = int(rating)
            review.comment = comment
            review.save()
            update_user_rating(review.to_user)
            messages.success(request, "Review updated successfully!")
        else:
            messages.error(request, "Invalid rating provided.")
            
        return redirect('reviews:user-written-reviews', user_id=request.user.id)

    return render(request, 'reviews/edit_review.html', {'review': review})


# --- AJAX Views (JSON Only) ---

@csrf_exempt # Tambahkan ini agar Flutter bisa POST data update
@login_required
def ajax_update_review(request, review_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': "Method not allowed"}, status=405)

    try:
        review = Review.objects.get(id=review_id)
        if review.from_user != request.user:
            return JsonResponse({'ok': False, 'error': "Forbidden"}, status=403)

        # Ambil data dari request.POST (format form-data)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', 'No comment')

        if rating:
            review.rating = int(rating)
            review.comment = comment
            review.save()
            update_user_rating(review.to_user)
            return JsonResponse({'ok': True})
            
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required
def ajax_create_event_reviews(request, event_id):
    """
    AJAX endpoint untuk submit multiple reviews sekaligus.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': "Method not allowed"}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'ok': False, 'error': "Event not found"}, status=404)

    from_user = request.user

    # Ambil peserta attended (kecuali diri sendiri)
    participants = User.objects.filter(
        joined_events__event=event,
        joined_events__status='attended'
    ).exclude(id=from_user.id)

    created_data = []
    skipped_ids = []

    # OPTIMASI: Pre-fetch existing reviews untuk event & user ini
    existing_reviews = set(
        Review.objects.filter(event=event, from_user=from_user)
        .values_list('to_user_id', flat=True)
    )

    for to_user in participants:
        # Check field form
        rating = request.POST.get(f'rating_{to_user.id}')
        comment = request.POST.get(f'comment_{to_user.id}', 'No comment')

        # Skip jika rating kosong
        if not rating:
            skipped_ids.append(to_user.id)
            continue

        # Skip jika sudah ada review (cegah duplikat)
        if to_user.id in existing_reviews:
            skipped_ids.append(to_user.id)
            continue

        try:
            rating_int = int(rating)
            if not (1 <= rating_int <= 5):
                raise ValueError()
        except ValueError:
            skipped_ids.append(to_user.id)
            continue

        # Create Review
        review = Review.objects.create(
            event=event,
            from_user=from_user,
            to_user=to_user,
            rating=rating_int,
            comment=comment
        )
        
        # Update statistic
        update_user_rating(to_user)

        created_data.append({
            'id': review.id,
            'to_user': to_user.username,
            'rating': review.rating,
            'comment': review.comment,
            'event_title': event.title,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({'ok': True, 'created': created_data, 'skipped': skipped_ids})

@login_required
def get_review_participants_api(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # 1. LOGIKA AMAN: Handle ID jika user belum login
    if request.user.is_authenticated:
        current_user_id = request.user.id
    else:
        current_user_id = -1 # Dummy ID agar query exclude tidak error

    # Ambil peserta (kecuali diri sendiri)
    participants = User.objects.filter(
        joined_events__event=event,
        joined_events__status='attended'
    ).exclude(id=current_user_id).select_related('profile')

    # 2. PERBAIKAN ERROR DISINI:
    # Jangan query Review jika user belum login (AnonymousUser tidak punya ID)
    existing_reviews = set()
    if request.user.is_authenticated:
        existing_reviews = set(
            Review.objects.filter(event=event, from_user=request.user)
            .values_list('to_user_id', flat=True)
        )

    data = []
    for user in participants:
        # Skip jika user ini sudah direview (hanya berlaku kalau sudah login)
        if user.id in existing_reviews:
            continue
            
        # Default Image (UI Avatars)
        image_url = f"https://ui-avatars.com/api/?name={user.username}&background=random"

        # Logika aman ambil foto profil (Try-Except)
        if hasattr(user, 'profile'):
            try:
                # Cek berbagai kemungkinan nama field gambar
                if hasattr(user.profile, 'image') and user.profile.image:
                    image_url = user.profile.image.url
                elif hasattr(user.profile, 'profile_image') and user.profile.profile_image:
                    image_url = user.profile.profile_image.url
                elif hasattr(user.profile, 'profile_image_url'):
                    val = user.profile.profile_image_url
                    result = val() if callable(val) else val
                    if result:
                        image_url = result
            except Exception:
                pass # Jika error, tetap pakai default UI Avatars

        data.append({
            'id': user.id,
            'username': user.username,
            'profile_image_url': image_url,
        })

    return JsonResponse({'participants': data})

@login_required
def get_my_reviews_json(request):
    """Mengambil semua review yang ditulis oleh user yang sedang login."""
    reviews = Review.objects.filter(from_user=request.user).select_related('to_user', 'event').order_by('-created_at')
    
    data = []
    for r in reviews:
        data.append({
            "id": r.id,
            "event_title": r.event.title,
            "reviewee_name": r.to_user.username,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.strftime('%Y-%m-%d'),
        })
    return JsonResponse({"status": "success", "data": data})

@csrf_exempt
@login_required
def ajax_delete_review(request, review_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': "Method not allowed"}, status=405)

    try:
        review = Review.objects.get(id=review_id)
        if review.from_user != request.user:
            return JsonResponse({'ok': False, 'error': "Forbidden"}, status=403)
        
        to_user = review.to_user
        review.delete()
        update_user_rating(to_user)
        return JsonResponse({'ok': True})
    except Review.DoesNotExist:
        return JsonResponse({'ok': False, 'error': "Review not found"}, status=404)
    
@login_required
def get_user_reviews_json(request, user_id):
    reviews = Review.objects.filter(to_user_id=user_id).select_related('from_user', 'event').order_by('-created_at')
    data = []
    for r in reviews:
        data.append({
            "id": r.id,
            "event_title": r.event.title,
            "reviewer_name": r.from_user.username, # Orang yang memberi nilai
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.strftime('%Y-%m-%d'),
        })
    return JsonResponse({"status": "success", "data": data})
