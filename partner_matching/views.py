from django.shortcuts import get_object_or_404, render
from sigma_app.constants import CITY_CHOICES, SPORT_CHOICES, SKILL_CHOICES
from django.db.models import Q
from django.contrib.auth.models import User

from authentication.models import UserProfile, SportPreference
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Connection

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from django.template.loader import render_to_string

def browse_user_ajax(request):

    users_query = User.objects.exclude(pk=request.user.pk).select_related('profile').prefetch_related('sport_preferences')

    search_query = request.GET.get('search', '')
    if search_query:
        users_query = users_query.filter(
            Q(username__icontains=search_query) |
            Q(profile__full_name__icontains=search_query)
        )

    city_filter = request.GET.get('city')
    if city_filter:
        users_query = users_query.filter(profile__city=city_filter)
    
    sport_filter = request.GET.get('sport')
    if sport_filter:
        users_query = users_query.filter(sport_preferences__sport_type=sport_filter)
    
    skill_filter = request.GET.get('skill')
    if skill_filter:
        users_query = users_query.filter(sport_preferences__skill_level=skill_filter)

    users_query = users_query.distinct()

    users_list = []

    DEFAULT_AVATAR = 'https://ui-avatars.com/api/?background=F26419&color=fff&size=96&name='

    for user in users_query:
        profile = getattr(user, 'profile', None)
        if not profile:
            continue
        
        sport_preferences = user.sport_preferences.all()
        sport_display = ", ".join([sp.sport_type for sp in sport_preferences]) if sport_preferences else "No Sports"
        
        profile_picture_url = ''
        
        # cek field yang ada di UserProfile 
        if hasattr(profile, 'profile_image_url') and profile.profile_image_url:
            # jika menggunakan URL field
            profile_picture_url = profile.profile_image_url
        elif hasattr(profile, 'photo') and profile.photo:
            # jika menggunakan ImageField
            try:
                profile_picture_url = profile.photo.url
            except:
                profile_picture_url = ''
        else:
            # fallback ke default avatar
            user_name = profile.full_name or user.username
            profile_picture_url = f"{DEFAULT_AVATAR}{user_name.replace(' ', '+')}"
        
        users_list.append({
            'id': user.id,
            'username': user.username,
            'full_name': profile.full_name,
            'city': profile.city,
            'profile_picture_url': profile_picture_url,
            'sports': sport_display,
        })

    return JsonResponse({'users': users_list})

@login_required
def browse_user(request):
    context = {
        'cities': CITY_CHOICES,
        'sports': SPORT_CHOICES,
        'skills': SKILL_CHOICES,
    }

    return render(request, 'partner_matching/browse.html', context)
    
@login_required
def user_profile_detail(request, user_id):
    # mendapatkan user berdasarkan user_id
    target_user = get_object_or_404(User, pk=user_id)

    # Get or create UserProfile if it doesn't exist
    try:
        target_profile = target_user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        target_profile = UserProfile.objects.create(
            user=target_user,
            full_name=target_user.get_full_name() or target_user.username,
            city='jakarta'  # default city
        )

    sport_preferences = SportPreference.objects.filter(user=target_user)

    connection_status = None

    is_friends = Connection.objects.filter(
        Q(from_user=request.user, to_user=target_user, status='accepted') |
        Q(from_user=target_user, to_user=request.user, status='accepted')
    ).exists()

    if is_friends:
        connection_status = 'accepted'
    else:
        # apakah ada request yang dikirim dari user ke target
        sent_request = Connection.objects.filter(
            from_user=request.user,
            to_user=target_user
        ).first()

        # apakah ada request yang diterima dari target ke user
        received_request = Connection.objects.filter(
            from_user=target_user,
            to_user=request.user
        ).first()

        if sent_request:
            # kalau ada request yang dikirim, status bisa pending/reject
            connection_status = 'pending'
        elif received_request:
            # kalau ada request yang diterima, status bisa pending/rejected
            connection_status = 'pending'
        else:
            # tidak ada koneksi sama sekali
            connection_status = None

    context = {
        'profile_user': target_user,
        'profile': target_profile,
        'sport_preferences': sport_preferences,
        'connection_status': connection_status,
    }

    return render(request, 'partner_matching/user_profile_detail.html', context)

@login_required
@require_http_methods(["POST"])
def connection_request(request, action, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    if request.user == target_user:
        return JsonResponse({'success': False, 'error': 'Cannot connect with yourself'})
    
    try:
        if action == 'connect':
            # create connection request
            connection, created = Connection.objects.get_or_create(
                from_user=request.user,
                to_user=target_user,
                defaults={'status': 'pending'}
            )
            
            if not created:
                return JsonResponse({'success': False, 'error': 'Connection request already exists'})
                
        elif action == 'accept':
            # accept incoming connection request
            connection = get_object_or_404(
                Connection, 
                from_user=target_user, 
                to_user=request.user,
                status='pending'
            )
            connection.status = 'accepted'
            connection.save()
            
        elif action == 'reject':
            # reject incoming connection request
            connection = get_object_or_404(
                Connection, 
                from_user=target_user, 
                to_user=request.user,
                status='pending'
            )
            connection.status = 'rejected'
            connection.save()
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def connections(request):
    # own profile connections view with tabs 
    try:
        # Friends: current user accepting requests from other users
        friends_who_sent_to_me = User.objects.filter(
            connections_sent__to_user=request.user,
            connections_sent__status='accepted'
        )
        
        # Friends: another user accepted current user request and the status is accepted
        friends_who_received_from_me = User.objects.filter(
            connections_received__from_user=request.user,
            connections_received__status='accepted'
        )
        
        my_friends = friends_who_sent_to_me.union(friends_who_received_from_me)
        
        # Received requests: Users who sent pending requests to current user
        received_requests = User.objects.filter(
            connections_sent__to_user=request.user,
            connections_sent__status='pending'
        )
        
        # Sent requests: Users who received pending requests from current user
        sent_requests = User.objects.filter(
            connections_received__from_user=request.user,
            connections_received__status='pending'
        )

        # excluded 
        excluded_users = User.objects.filter(
            Q(connections_sent__to_user=request.user) |
            Q(connections_received__from_user=request.user) |
            Q(id=request.user.id)
        ).distinct()

        user_sports = SportPreference.objects.filter(user=request.user).values_list('sport_type', flat=True)

        user_city = request.user.profile.city if hasattr(request.user, 'profile') else None
        
        recommendations = User.objects.exclude(
            id__in=excluded_users.values_list('id', flat=True)
        ).filter(sport_preferences__sport_type__in=user_sports).distinct()

        # add match score to each user
        recommendations_with_score = []
        for user in recommendations:
            score = calculate_match_score(request.user, user)
            if score > 0:  # only include users with some match
                recommendations_with_score.append({
                    'user': user,
                    'score': score,
                    'common_sports': get_common_sports(request.user, user),
                    'same_city': user_city and hasattr(user, 'profile') and user.profile.city == user_city
                })

            recommendations_with_score.sort(key=lambda x: x['score'], reverse=True)

        context = {
            'my_friends': my_friends,
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'is_own_connections': True,
            'recommendations': recommendations_with_score,
        }
        return render(request, 'partner_matching/connections.html', context)
        
    except Exception as e:
        print(f"Error in connections view: {e}")
        context = {
            'my_friends': User.objects.none(),
            'received_requests': User.objects.none(),
            'sent_requests': User.objects.none(),
            'is_own_connections': True,
        }
        return render(request, 'partner_matching/connections.html', context)
    
def calculate_match_score(user1, user2):
    score = 0

    common_sports = get_common_sports(user1, user2)
    score += min(len(common_sports) * 10, 40) # max point 40

    if (hasattr(user1, 'profile') and hasattr(user2, 'profile') and user1.profile.city == user2.profile.city):
        score += 30 # same city 30

    skill_score = calculate_skill_compatibility(user1, user2, common_sports)
    score += skill_score

    return score

def get_common_sports(user1, user2):
    user1_sports = set(SportPreference.objects.filter(user=user1).values_list('sport_type', flat=True))
    user2_sports = set(SportPreference.objects.filter(user=user2).values_list('sport_type', flat=True))
    return list(user1_sports.intersection(user2_sports))

def calculate_skill_compatibility(user1, user2, common_sport):
    if not common_sport:
        return 0
    
    skill_levels = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3,
        'pro': 4
    }

    total_compatibility = 0

    for sport in common_sport:
        try:
            user1_pref = SportPreference.objects.get(user=user1, sport_type=sport)
            user2_pref = SportPreference.objects.get(user=user2, sport_type=sport)

            level_user1 = skill_levels.get(user1_pref.skill_level, 0)
            level_user2 = skill_levels.get(user2_pref.skill_level, 0)

            level_diff = abs(level_user1 - level_user2)
            if level_diff == 0:  
                total_compatibility += 10
            elif level_diff == 1: 
                total_compatibility += 7
            elif level_diff == 2:  
                total_compatibility += 3
            else:
                total_compatibility += 0
        except SportPreference.DoesNotExist:
            continue

        return min(total_compatibility, 30)

def public_connections(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    try:
        friends_from_received = User.objects.filter(
            connections_received__to_user=target_user,
            connections_received__status='accepted'
        )

        friends_from_sent = User.objects.filter(
            connections_sent__from_user=target_user,
            connections_sent__status='accepted'
        )

        friends = friends_from_received.union(friends_from_sent)

        context = {
            'target_user': target_user,
            'friends': friends,
            'is_own_connections': False,
        }

        return render(request, 'partner_matching/connections.html', context)

    except Exception as e:
        print("Error fetching public connections:", str(e))
        context = {
            'target_user': target_user,
            'friends': [],
            'is_own_connections': False,
        }

        return render(request, 'partner_matching/connections.html', context)

@csrf_exempt 
@login_required
def connection_action_by_user(request, action, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        if action == 'connect':
            # user mengirim request ke target_user
            connection, created = Connection.objects.get_or_create(
                from_user=request.user,
                to_user=target_user,
                defaults={'status': 'pending'}
            )
            if not created:
                return JsonResponse({'success': False, 'error': 'Connection request already exists'})
        elif action == 'accept':
            # user menerima request dari target_user
            connection = Connection.objects.filter(
                from_user=target_user, 
                to_user=request.user,
                status='pending'
            ).first()
            if not connection:
                return JsonResponse({'success': False, 'error': 'No pending request found'})
            connection.status = 'accepted'
            connection.save()
                
        elif action == 'reject':
            # user menolak request dari target_user
            connection = Connection.objects.filter(
                from_user=target_user, 
                to_user=request.user,
                status='pending'
            ).first()
            if not connection:
                return JsonResponse({'success': False, 'error': 'No pending request found'})
            connection.status = 'rejected'
            connection.save()
                
        elif action == 'remove':
            # user remove friend (accepted connection)
            connection = Connection.objects.filter(
                Q(from_user=request.user, to_user=target_user, status='accepted') |
                Q(from_user=target_user, to_user=request.user, status='accepted')
            ).first()
            if not connection:
                return JsonResponse({'success': False, 'error': 'No friendship found'})
            connection.delete()
                
        elif action == 'cancel':
            # user cancel sent request
            connection = Connection.objects.filter(
                from_user=request.user, 
                to_user=target_user,
                status='pending'
            ).first()
            if not connection:
                return JsonResponse({'success': False, 'error': 'No sent request found'})
            connection.delete()
                
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Error in connection_action_by_user: {e}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def connections_api(request):
    try:
        friends_who_sent_to_me = User.objects.filter(
            connections_sent__to_user=request.user,
            connections_sent__status='accepted'
        )
        friends_who_received_from_me = User.objects.filter(
            connections_received__from_user=request.user,
            connections_received__status='accepted'
        )
        my_friends = friends_who_sent_to_me.union(friends_who_received_from_me)
        
        received_requests = User.objects.filter(
            connections_sent__to_user=request.user,
            connections_sent__status='pending'
        )
        sent_requests = User.objects.filter(
            connections_received__from_user=request.user,
            connections_received__status='pending'
        )

        excluded_users = User.objects.filter(
            Q(connections_sent__to_user=request.user) |
            Q(connections_received__from_user=request.user) |
            Q(id=request.user.id)
        ).distinct()

        user_sports = SportPreference.objects.filter(user=request.user).values_list('sport_type', flat=True)
        user_city = request.user.profile.city if hasattr(request.user, 'profile') else None
        
        recommendations = User.objects.exclude(
            id__in=excluded_users.values_list('id', flat=True)
        ).filter(sport_preferences__sport_type__in=user_sports).distinct()

        def serialize_user(user, extra_data=None):
            profile = getattr(user, 'profile', None)
            pic_url = '/static/images/default-avatar.png'
            if profile:
                if hasattr(profile, 'profile_image_url') and profile.profile_image_url:
                    pic_url = profile.profile_image_url
                elif hasattr(profile, 'photo') and profile.photo:
                    pic_url = profile.photo.url
            
            data = {
                'id': user.id,
                'username': user.username,
                'full_name': profile.full_name if profile else user.username,
                'city': profile.city if profile else 'Unknown',
                'profile_picture_url': pic_url,
                'sports': list(user.sport_preferences.values_list('sport_type', flat=True))
            }
            if extra_data:
                data.update(extra_data)
            return data

        friends_data = [serialize_user(u) for u in my_friends]

        received_data = [serialize_user(u) for u in received_requests]

        sent_data = [serialize_user(u) for u in sent_requests]

        recommendations_data = []
        for user in recommendations:
            score = calculate_match_score(request.user, user)
            if score > 0:
                rec_info = serialize_user(user, extra_data={
                    'score': score,
                    'common_sports': get_common_sports(request.user, user),
                    'same_city': user_city and hasattr(user, 'profile') and user.profile.city == user_city
                })
                recommendations_data.append(rec_info)
        
        recommendations_data.sort(key=lambda x: x['score'], reverse=True)

        return JsonResponse({
            'status': 'success',
            'my_friends': friends_data,
            'received_requests': received_data,
            'sent_requests': sent_data,
            'recommendations': recommendations_data
        })

    except Exception as e:
        print(f"Error in connections_api: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def get_filter_options_api(request):
    def map_choices(choices):
        return [{'value': key, 'label': label} for key, label in choices]

    data = {
        'cities': map_choices(CITY_CHOICES),
        'sports': map_choices(SPORT_CHOICES),
        'skills': map_choices(SKILL_CHOICES),
    }

    return JsonResponse(data)

@login_required
def user_profile_detail_api(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    try:
        target_profile = target_user.profile
    except UserProfile.DoesNotExist:
        target_profile = UserProfile.objects.create(
            user=target_user,
            full_name=target_user.get_full_name() or target_user.username,
            city='jakarta'
        )

    sport_preferences = SportPreference.objects.filter(user=target_user)
    sports_data = []
    for sp in sport_preferences:
        sports_data.append({
            'id': sp.id,
            'sport_type': sp.sport_type,
            'skill_level': sp.skill_level,
        })

    connection_status = 'none'

    is_friends = Connection.objects.filter(
        Q(from_user=request.user, to_user=target_user, status='accepted') |
        Q(from_user=target_user, to_user=request.user, status='accepted')
    ).exists()

    if is_friends:
        connection_status = 'accepted'
    else:
        sent_request = Connection.objects.filter(
            from_user=request.user,
            to_user=target_user,
            status='pending'
        ).exists()

        received_request = Connection.objects.filter(
            from_user=target_user,
            to_user=request.user,
            status='pending'
        ).exists()

        if sent_request:
            connection_status = 'pending_sent'
        elif received_request:
            connection_status = 'pending_received'

    pic_url = '/static/images/default-avatar.png'
    if hasattr(target_profile, 'profile_image') and target_profile.profile_image:
        pic_url = target_profile.profile_image.url
    elif hasattr(target_profile, 'photo') and target_profile.photo:
        pic_url = target_profile.photo.url
    elif hasattr(target_profile, 'profile_image_url') and target_profile.profile_image_url:
        pic_url = target_profile.profile_image_url

    data = {
        'status': True,
        'data': {
            'id': target_user.id,
            'username': target_user.username,
            'full_name': target_profile.full_name,
            'city': target_profile.city,
            'bio': getattr(target_profile, 'bio', ''),
            'profile_picture_url': pic_url,
            'connection_status': connection_status,
            'sport_preferences': sports_data,
        }
    }

    return JsonResponse(data)

@login_required
def public_connections_api(request, user_id):
    """API endpoint to fetch public connections for a specific user"""
    target_user = get_object_or_404(User, id=user_id)

    try:
        # Get friends who sent requests to target user
        friends_from_received = User.objects.filter(
            connections_received__to_user=target_user,
            connections_received__status='accepted'
        )

        # Get friends who received requests from target user
        friends_from_sent = User.objects.filter(
            connections_sent__from_user=target_user,
            connections_sent__status='accepted'
        )

        # Combine both querysets
        friends = friends_from_received.union(friends_from_sent)

        # Serialize user data
        def serialize_user(user):
            profile = getattr(user, 'profile', None)
            pic_url = '/static/images/default-avatar.png'
            if profile:
                if hasattr(profile, 'profile_image_url') and profile.profile_image_url:
                    pic_url = profile.profile_image_url
                elif hasattr(profile, 'photo') and profile.photo:
                    pic_url = profile.photo.url

            return {
                'id': user.id,
                'username': user.username,
                'full_name': profile.full_name if profile else user.username,
                'city': profile.city if profile else 'Unknown',
                'profile_picture_url': pic_url,
                'sports': list(user.sport_preferences.values_list('sport_type', flat=True))
            }

        friends_data = [serialize_user(u) for u in friends]

        return JsonResponse({
            'status': 'success',
            'my_friends': friends_data
        })

    except Exception as e:
        print(f"Error in public_connections_api: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

