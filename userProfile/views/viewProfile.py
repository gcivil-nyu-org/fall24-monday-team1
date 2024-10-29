from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ..models import UserProfile
import json
import boto3 
import os
from gamesearch.views import authorize_igdb
import requests

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt



def viewProfile(request, user_id):
    # Retrieve the user profile based on the user_id
    profile = get_object_or_404(UserProfile, user__id=user_id)

    viewable = False

    if (profile.user == request.user):
        viewable = True
    if (profile.privacy_setting == "public"):
        viewable = True
    if (profile.privacy_setting == "friends_only"):
        pass
    
    # Prepare the context with the profile data
    gaming_usernames = None
    if profile.gaming_usernames:
        try:
            gaming_usernames = json.loads(profile.gaming_usernames)
        except TypeError:
            gaming_usernames = profile.gaming_usernames

    context = {
        'profile': profile,
        'viewable': viewable,
        'gaming_usernames': gaming_usernames,
        'own' : profile.user == request.user,
        'loginIn' : request.user.is_authenticated,
        'curPath' : reverse('userProfile:viewProfile', args=[profile.user.pk]),
    }

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    # Reference the DynamoDB table
    table = dynamodb.Table('user-shelves')
    try:
        response = table.get_item(Key={'user_id' : profile.user.username})
        if 'Item' in response:
            user_games = response['Item']
            del user_games["user_id"]
            context['user_games'] = user_games
        else:
            print("no games were found for this user!")
    except Exception as e:
        print(e)

    return render(request, 'profileView.html', context)

@login_required
def viewMyProfile(request):
    return viewProfile(request, request.user.pk)


@csrf_exempt
@require_POST
def fetch_game_details(request):
    game_ids = request.POST.getlist('gameIds[]')  # Retrieve as a list
    game_id_string = f"({','.join(game_ids)})"  # Format as (gameid1, gameid2, ...)
    print(game_ids)
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
