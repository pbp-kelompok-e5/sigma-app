from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum
from authentication.models import UserProfile

def leaderboard_page(request):
    """
    MVP Leaderboard Page - menampilkan ranking user berdasarkan total points
    """
    
    # Get filter dari query params (default: all_time)
    period_filter = request.GET.get('period', 'all_time')
    sport_filter = request.GET.get('sport', '')
    
    # Query users dengan points, diurutkan descending
    users_list = UserProfile.objects.select_related('user').order_by('-total_points')
    
    # Add ranking ke setiap user
    ranked_users = []
    for idx, profile in enumerate(users_list, start=1):
        ranked_users.append({
            'rank': idx,
            'user_id': profile.user.id,
            'full_name': profile.full_name,
            'username': profile.user.username,
            'total_points': profile.total_points,
            'total_events': profile.total_events,
            'city': profile.get_city_display(),
            'profile_image_url': profile.profile_image_url or '/static/img/default-avatar.png',
            'tier': get_tier(profile.total_points),
            'badge': get_badge(profile.total_points),
        })
    
    context = {
        'users': ranked_users,
        'current_filter': period_filter,
        'sport_filter': sport_filter,
    }
    
    return render(request, 'leaderboard/leaderboard.html', context)


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
