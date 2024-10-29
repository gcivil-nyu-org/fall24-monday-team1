from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ..models import UserProfile
import json
import boto3 
import os

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


def fetch_user_games(request, username):
    if request.method == "GET":
        print(username)