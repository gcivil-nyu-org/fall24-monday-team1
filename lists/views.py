from django.shortcuts import render
import requests
from django.http import JsonResponse
import os
from gamesearch.views import authorize_igdb
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import boto3
import uuid
import urllib

@login_required
def create_list(request):
    return render(request, 'create_list.html')

@csrf_exempt
def search_igdb_games(request):
    query = request.POST.get('query', '')
    if not query:
        return JsonResponse([], safe=False)

    auth = authorize_igdb()
    headers = {
        'Client-ID': os.environ.get("igdb_client_id"),
        'Authorization': f'Bearer {auth.json()["access_token"]}',
        'Content-Type': 'text/plain',
    }
    payload = f'search "{query}"; fields name;'
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=payload)
    games = response.json()
    return JsonResponse(games, safe=False)



@login_required
@csrf_exempt
def save_list(request):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('lists')

    if request.method == 'POST':
        try:
            data = dict(request.POST)
            print(data)
            username = request.user.username  # Get the current user's username

            # Prepare the item to be saved in DynamoDB
            item = {
                'listId': str(uuid.uuid4()),
                'username': username,
                'name': data['name'],
                'description': data['description'],
                'visibility': data['visibility'],
                'games': data['games[]']
            }
            
            try:
                table.put_item(Item=item)
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'failedToPutToDynamo'})


            return JsonResponse({'status': 'success'})
        
        except Exception as e:
            return JsonResponse({"status": "error"})
    else:
        return JsonResponse({"status": "error"})