from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from authentication.models import UserProfile
from leaderboard.models import PointTransaction, Achievement


def leaderboard_page(request):
    """
    Leaderboard Page - menampilkan ranking user berdasarkan total points
    dengan filter periode
    """
    from django.utils import timezone
    from datetime import timedelta

    # Get filter dari query params
    period_filter = request.GET.get('period', 'all_time')

    # Query all user profiles
    profiles_query = UserProfile.objects.select_related('user').all()

    # Build ranked users list with period filtering
    ranked_users = []
    for profile in profiles_query:
        # Calculate points based on period
        if period_filter == 'all_time':
            points = profile.total_points
        else:
            # Filter point transactions by period
            now = timezone.now()
            if period_filter == 'weekly':
                start_date = now - timedelta(days=7)
            elif period_filter == 'monthly':
                start_date = now - timedelta(days=30)
            else:
                start_date = None

            if start_date:
                period_points = PointTransaction.objects.filter(
                    user=profile.user,
                    created_at__gte=start_date
                ).aggregate(Sum('points'))['points__sum'] or 0
                points = period_points
            else:
                points = profile.total_points

        # Include all users, even with 0 points
        ranked_users.append({
            'user_id': profile.user.id,
            'full_name': profile.full_name,
            'username': profile.user.username,
            'total_points': points,
            'total_events': profile.total_events,
            'city': profile.get_city_display() if profile.city else 'Unknown',
            'profile_image_url': profile.profile_image_url or '/static/img/default-avatar.png',
            'tier': get_tier(points),
            'badge': get_badge(points),
        })

    # Sort by points and assign ranks
    ranked_users.sort(key=lambda x: x['total_points'], reverse=True)
    for rank, user_data in enumerate(ranked_users, start=1):
        user_data['rank'] = rank

    # Get current user's rank if logged in
    current_user_rank = None
    if request.user.is_authenticated:
        for user_data in ranked_users:
            if user_data['user_id'] == request.user.id:
                current_user_rank = user_data['rank']
                break

    context = {
        'users': ranked_users,
        'current_filter': period_filter,
        'current_user_rank': current_user_rank,
    }

    return render(request, 'leaderboard/leaderboard.html', context)


def leaderboard_api(request):
    """
    AJAX API endpoint for leaderboard data
    Supports filtering by period
    """
    from django.utils import timezone
    from datetime import timedelta

    # Get filter and pagination params
    period_filter = request.GET.get('period', 'all_time')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))

    # Query all user profiles
    profiles_query = UserProfile.objects.select_related('user').all()

    # Build ranked users list with period filtering
    ranked_users = []
    for profile in profiles_query:
        # Calculate points based on period
        if period_filter == 'all_time':
            points = profile.total_points
        else:
            # Filter point transactions by period
            now = timezone.now()
            if period_filter == 'weekly':
                start_date = now - timedelta(days=7)
            elif period_filter == 'monthly':
                start_date = now - timedelta(days=30)
            else:
                start_date = None

            if start_date:
                period_points = PointTransaction.objects.filter(
                    user=profile.user,
                    created_at__gte=start_date
                ).aggregate(Sum('points'))['points__sum'] or 0
                points = period_points
            else:
                points = profile.total_points

        # Include all users, even with 0 points
        ranked_users.append({
            'user_id': profile.user.id,
            'full_name': profile.full_name,
            'username': profile.user.username,
            'total_points': points,
            'total_events': profile.total_events,
            'city': profile.get_city_display() if profile.city else 'Unknown',
            'profile_image_url': profile.profile_image_url or '/static/img/default-avatar.png',
            'tier': get_tier(points),
            'badge': get_badge(points),
        })

    # Sort by points and assign ranks
    ranked_users.sort(key=lambda x: x['total_points'], reverse=True)
    for rank, user_data in enumerate(ranked_users, start=1):
        user_data['rank'] = rank

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = ranked_users[start:end]

    # Get current user's rank if logged in
    current_user_rank = None
    if request.user.is_authenticated:
        for user_data in ranked_users:
            if user_data['user_id'] == request.user.id:
                current_user_rank = user_data['rank']
                break

    return JsonResponse({
        'success': True,
        'users': paginated_users,
        'total_count': len(ranked_users),
        'page': page,
        'per_page': per_page,
        'current_user_rank': current_user_rank,
    })


@login_required(login_url='login')
def points_dashboard(request):
    """
    Points Dashboard - menampilkan total points dan breakdown aktivitas user
    """
    user = request.user
    profile = get_object_or_404(UserProfile, user=user)

    # Get all point transactions
    transactions = PointTransaction.objects.filter(user=user).order_by('-created_at')

    # Calculate breakdown by activity type
    breakdown = {}
    for activity_type, label in PointTransaction.ACTIVITY_CHOICES:
        total = transactions.filter(activity_type=activity_type).aggregate(Sum('points'))['points__sum'] or 0
        count = transactions.filter(activity_type=activity_type).count()
        breakdown[activity_type] = {
            'label': label,
            'total': total,
            'count': count,
        }

    # Get recent transactions (last 10)
    recent_transactions = transactions[:10]

    # Get user's achievements
    achievements = Achievement.objects.filter(user=user).order_by('-earned_at')

    # Get user's rank
    ranked_users = UserProfile.objects.order_by('-total_points')
    user_rank = None
    for idx, p in enumerate(ranked_users, start=1):
        if p.user.id == user.id:
            user_rank = idx
            break

    context = {
        'profile': profile,
        'total_points': profile.total_points,
        'total_events': profile.total_events,
        'breakdown': breakdown,
        'recent_transactions': recent_transactions,
        'achievements': achievements,
        'user_rank': user_rank,
        'tier': get_tier(profile.total_points),
        'badge': get_badge(profile.total_points),
    }

    return render(request, 'leaderboard/points_dashboard.html', context)


@login_required(login_url='login')
def points_history(request):
    """
    Points History - menampilkan semua transaksi poin user
    """
    user = request.user

    # Get all transactions with pagination
    transactions = PointTransaction.objects.filter(user=user).order_by('-created_at')

    # Filter by activity type if provided
    activity_filter = request.GET.get('activity', '')
    if activity_filter:
        transactions = transactions.filter(activity_type=activity_filter)

    context = {
        'transactions': transactions,
        'activity_filter': activity_filter,
        'activity_choices': PointTransaction.ACTIVITY_CHOICES,
    }

    return render(request, 'leaderboard/points_history.html', context)


@login_required(login_url='login')
def achievements_page(request):
    """
    Achievements Page - menampilkan achievements user
    """
    user = request.user

    # Get user's achievements
    earned_achievements = Achievement.objects.filter(user=user).order_by('-earned_at')

    # Get all possible achievements
    all_achievement_codes = [code for code, _ in Achievement.ACHIEVEMENT_CODES]
    earned_codes = set(earned_achievements.values_list('achievement_code', flat=True))

    # Create list of all achievements with earned status
    all_achievements = []
    for code, title in Achievement.ACHIEVEMENT_CODES:
        is_earned = code in earned_codes
        earned_ach = earned_achievements.filter(achievement_code=code).first() if is_earned else None

        all_achievements.append({
            'code': code,
            'title': title,
            'is_earned': is_earned,
            'earned_at': earned_ach.earned_at if earned_ach else None,
            'bonus_points': earned_ach.bonus_points if earned_ach else 0,
            'description': earned_ach.description if earned_ach else get_achievement_description(code),
        })

    context = {
        'all_achievements': all_achievements,
        'earned_count': len(earned_codes),
        'total_count': len(all_achievement_codes),
        'earned_percent': (len(earned_codes) / len(all_achievement_codes) * 100) if all_achievement_codes else 0,
    }

    return render(request, 'leaderboard/achievements.html', context)


def get_tier(points):
    """Helper function untuk menentukan tier berdasarkan points"""
    if points >= 1000:
        return 'Master'
    elif points >= 500:
        return 'Expert'
    elif points >= 200:
        return 'Advanced'
    elif points >= 50:
        return 'Intermediate'
    else:
        return 'Beginner'


def get_badge(points):
    """Helper function untuk menentukan badge emoji"""
    if points >= 1000:
        return '🥇'
    elif points >= 500:
        return '🥈'
    elif points >= 200:
        return '🥉'
    elif points >= 50:
        return '⭐'
    else:
        return '🔰'


def get_achievement_description(code):
    """Get description for achievement code"""
    descriptions = {
        'first_event': 'Join your first event',
        'ten_events': 'Complete 10 events',
        'organizer': 'Organize 5 events',
        'highly_rated': 'Receive 10 five-star reviews',
        'social_butterfly': 'Make 20 connections',
        'early_bird': 'Join 5 morning events',
    }
    return descriptions.get(code, 'Unknown achievement')
