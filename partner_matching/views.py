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

# Create your views here.
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
    for user in users_query:
        profile = getattr(user, 'profile', None)
        if not profile:
            continue
        
        sport_preferences = user.sport_preferences.all()
        sport_display = ", ".join([sp.sport_type for sp in sport_preferences]) if sport_preferences else "No Sports"
        
        # FIX: Handle profile picture based on actual model fields
        profile_picture_url = ''
        
        # Cek field yang ada di UserProfile model Anda
        if hasattr(profile, 'profile_image_url') and profile.profile_image_url:
            # Jika menggunakan URL field
            profile_picture_url = profile.profile_image_url
        elif hasattr(profile, 'photo') and profile.photo:
            # Jika menggunakan ImageField
            try:
                profile_picture_url = profile.photo.url
            except:
                profile_picture_url = ''
        else:
            # Fallback ke default avatar
            profile_picture_url = '/static/images/default-avatar.png'
        
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

    # print("SPORT_CHOICES:", SPORT_CHOICES)

    return render(request, 'partner_matching/browse.html', context)
    
@login_required
def user_profile_detail(request, user_id):
    # mendapatkan user berdasarkan user_id
    target_user = get_object_or_404(User, pk=user_id)
    target_profile = get_object_or_404(UserProfile, user=target_user)

    sport_preferences = SportPreference.objects.filter(user=target_user)

    # cek koneksi antara user saat ini dan target_user
    connection_status = None

    connection = Connection.objects.filter(
        from_user=request.user, to_user=target_user
    ).first()

    if connection:
        connection_status = connection.status  # 'pending' or 'accepted' or 'rejected'
    else:
        incoming_connection = Connection.objects.filter(
            from_user=target_user, to_user=request.user
        ).first()
        if incoming_connection:
            connection_status = 'incoming'
    
    context = {
        'profile_user': target_user,
        'profile': target_profile,
        'sport_preferences': sport_preferences,
        'connection_status': connection_status,
        'connection': connection,
        'connection_status': connection_status,
    }

    return render(request, 'partner_matching/user_profile_detail.html', context)

# @login_required
# def user_profile_detail(request, user_id):
#     target_user = get_object_or_404(User, id=user_id)
#     target_profile = get_object_or_404(UserProfile, user=target_user)
    
#     is_own_profile = (request.user == target_user)
#     sport_preferences = SportPreference.objects.filter(user=target_user)
    
#     # connection logic
#     connection_status = None
    
#     if not is_own_profile:
#         # check if current user sent a request to target user
#         sent_request = Connection.objects.filter(
#             from_user=request.user,
#             to_user=target_user
#         ).first()
        
#         if sent_request:
#             connection_status = sent_request.status  # 'pending' or 'accepted'
#         else:
#             # Check if target user sent a request to current user  
#             received_request = Connection.objects.filter(
#                 from_user=target_user,
#                 to_user=request.user,
#                 status='pending'
#             ).first()
            
#             if received_request:
#                 connection_status = 'incoming'
    
#     context = {
#         'profile_user': target_user,
#         'profile': target_profile,
#         'sport_preferences': sport_preferences,
#         'is_own_profile': is_own_profile,
#         'connection_status': connection_status,
#     }
    
#     return render(request, 'partner_matching/user_profile_detail.html', context)

@login_required
@require_http_methods(["POST"])
def connection_request(request, action, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    if request.user == target_user:
        return JsonResponse({'success': False, 'error': 'Cannot connect with yourself'})
    
    try:
        if action == 'connect':
            # Create connection request
            connection, created = Connection.objects.get_or_create(
                from_user=request.user,
                to_user=target_user,
                defaults={'status': 'pending'}
            )
            
            if not created:
                return JsonResponse({'success': False, 'error': 'Connection request already exists'})
                
        elif action == 'accept':
            # Accept incoming connection request
            connection = get_object_or_404(
                Connection, 
                from_user=target_user, 
                to_user=request.user,
                status='pending'
            )
            connection.status = 'accepted'
            connection.save()
            
        elif action == 'reject':
            # Reject incoming connection request
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

def icon_preview(request):
    from sigma_app.templatetags.icon_tags import get_available_icons, get_size_presets, get_color_presets
    
    context = {
        'available_icons': get_available_icons(),
        'size_presets': get_size_presets(),
        'color_presets': get_color_presets(),
    }
    return render(request, 'partner_matching/icons_preview.html', context)

@login_required
def connection(request):
    my_friends = User.objects.filter(
        Q(connections_sent__to_user=request.user, connections_sent__status='accepted') |
        Q(connections_received__from_user=request.user, connections_received__status='accepted')
    ).distinct()

    received_requests = Connection.objects.filter(
        connections_sent__to_user=request.user, connections_sent__status='pending'
    ).distinct()

    sent_requests = Connection.objects.filter(
        connections_received__from_user=request.user, connections_received__status='pending'
    ).distinct()

    context = {
        'my_friends': my_friends,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'is_own_connections': True,
    }

    return render(request, 'partner_matching/connections.html', context)

def public_connection(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    friends = User.objects.filter(
        Q(connections_sent__to_user=target_user, connections_sent__status='accepted') |
        Q(connections_received__from_user=target_user, connections_received__status='accepted')
    ).distinct()

    context = {
        'target_user': target_user,
        'friends': friends,
        'is_own_connections': False,
    }

    return render(request, 'partner_matching/connections.html', context)

@login_required
def connection_action(request, action, connection_id):
    connection = get_object_or_404(Connection, id=connection_id)

    if connection.from_user != request.user and connection.to_user != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    try:
        if action == 'accept':
            if connection.to_user == request.user and connection.status == 'pending':
                connection.status = 'accepted'
                connection.save()
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
        
        elif action == 'reject':
            if connection.to_user == request.user and connection.status == 'pending':
                connection.status = 'rejected'
                connection.save()
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
            
        elif action == 'remove':
            if (connection.from_user == request.user or connection.to_user == request.user) and connection.status == 'accepted':
                connection.delete()
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def connections(request):
    """Own profile connections view with tabs - CORRECTED"""
    try:
        # Friends: Users who have accepted connections with current user
        friends_who_sent_to_me = User.objects.filter(
            connections_sent__to_user=request.user,
            connections_sent__status='accepted'
        )
        
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
        
        context = {
            'my_friends': my_friends,
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'is_own_connections': True,
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
    
@login_required
def connection_action_by_user(request, action, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        if action == 'accept':
            # User menerima request dari target_user
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
            # User menolak request dari target_user
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
            # User remove friend (accepted connection)
            connection = Connection.objects.filter(
                Q(from_user=request.user, to_user=target_user, status='accepted') |
                Q(from_user=target_user, to_user=request.user, status='accepted')
            ).first()
            if not connection:
                return JsonResponse({'success': False, 'error': 'No friendship found'})
            connection.delete()
                
        elif action == 'cancel':
            # User cancel sent request
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
    