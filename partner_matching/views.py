from django.shortcuts import render
from sigma_app.constants import CITY_CHOICES, SPORT_CHOICES, SKILL_CHOICES
from django.db.models import Q
from django.contrib.auth.models import User

from authentication.models import UserProfile, SportPreference
from django.forms.models import model_to_dict
from django.http import JsonResponse

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

        users_list.append({
            'id' : user.id,
            'username': user.username,
            'full_name': user.profile.full_name,
            'city': user.profile.city,
            'profile_picture_url': user.profile.photo.url,
            'sports': sport_display,
        })

    return JsonResponse({'users': users_list})

def browse_user(request):
    context = {
        'cities': CITY_CHOICES,
        'sports': SPORT_CHOICES,
        'skills': SKILL_CHOICES,
    }

    # print("SPORT_CHOICES:", SPORT_CHOICES)

    return render(request, 'partner_matching/browse.html', context)
    

    
