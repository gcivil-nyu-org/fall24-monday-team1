from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ..models import UserProfile
from friends.models import FriendRequest
import json
import boto3 
import os
from gamesearch.views import authorize_igdb
import requests
from unittest import skip
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt



def viewProfile(request, user_id):
    try:
        profile = get_object_or_404(UserProfile, user_id=user_id)
    except Http404:
        if (user_id == request.user.pk):
            return redirect('createUserProfile:createProfile')
        raise Http404("UserProfile not found for the given user_id.")
    
    # Initialize variables
    is_own_profile = request.user.id == user_id
    is_friend = False
    has_sent_request = False
    has_received_request = False
    viewable = False
    friends = []

    if request.user.is_authenticated:
        friends = FriendRequest.get_friends(request.user.username)
        
        if not is_own_profile:
            # Check friendship status
            is_friend = any(friend['username'] == profile.user.username for friend in friends)
            
            # Check for sent requests
            sent_requests = FriendRequest.get_sent_requests(request.user.username)
            has_sent_request = any(req['to_user'] == profile.user.username for req in sent_requests)
            
            # Check for received requests
            received_requests = FriendRequest.get_pending_requests(request.user.username)
            has_received_request = any(req['from_user'] == profile.user.username for req in received_requests)

    # Check profile visibility
    if is_own_profile or profile.privacy_setting == "public":
        viewable = True
    elif profile.privacy_setting == "friends_only" and is_friend:
        viewable = True

    # Prepare gaming usernames
    gaming_usernames = None
    if profile.gaming_usernames:
        try:
            gaming_usernames = json.loads(profile.gaming_usernames)
        except TypeError:
            gaming_usernames = profile.gaming_usernames

    # Create context with all necessary data
    context = {
        'profile': profile,
        'viewable': viewable,
        'gaming_usernames': gaming_usernames,
        'own': is_own_profile,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'has_sent_request': has_sent_request,
        'has_received_request': has_received_request,
        'loginIn': request.user.is_authenticated,
        'friends': friends,
        'curPath': reverse('userProfile:viewProfile', args=[profile.user.pk]),
    }

    # Add user games to context
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        table = dynamodb.Table('user-shelves')
        response = table.get_item(Key={'user_id': profile.user.username})
        if 'Item' in response:
            user_games = response['Item']
            del user_games["user_id"]
            context['user_games'] = user_games
        else:
            context['user_games'] = {
                'want-to-play': [],
                'completed': [],
                "abandoned": [],
                "playing": [],
                "paused": []
            }
    except Exception as e:
        print(e)

    return render(request, 'profileView.html', context)

@login_required
def viewMyProfile(request):
    return viewProfile(request, request.user.pk)


@csrf_exempt
@require_POST

def fetch_game_details(request):    #pragma: no cover
    game_ids = request.POST.getlist('gameIds[]')  # Retrieve as a list
    game_id_string = f"({','.join(game_ids)})"  # Format as (gameid1, gameid2, ...)
    # print(game_ids)
    auth=authorize_igdb()

    game_details_url = 'https://api.igdb.com/v4/games'
    headers = {
        'Client-ID': os.environ.get('igdb_client_id'),
        'Authorization': f'Bearer {auth.json()["access_token"]}',
        'Content-Type': 'text/plain'
    }
    payload = f'fields name, cover; where id={game_id_string};'
    game_response = requests.post(game_details_url, headers=headers, data=payload)
    game_details = game_response.json()
    data = []
    for game in game_details:
        row = {}
        url = "https://api.igdb.com/v4/covers"
        payload = "fields url; where id=%d;" % (game['cover'])
        response = requests.request("POST", url, headers=headers, data=payload)
        img_url = response.json()[0]["url"].split("//")[1]

        row["cover"] = img_url
        row["name"] = game["name"]
        row["id"] = game['id']
        row["redirect_url"] = reverse('gamesearch:game-details', args=[int(game['id'])])
        data.append(row)
    
    return JsonResponse(data, safe=False)
