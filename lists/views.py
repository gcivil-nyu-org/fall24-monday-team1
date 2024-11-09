from django.shortcuts import render
import requests
from django.http import JsonResponse
import os
from gamesearch.views import authorize_igdb
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import boto3
import uuid
from django.core.paginator import Paginator
from boto3.dynamodb.conditions import Attr


@login_required
def create_list(request):
    return render(request, 'create_list.html')

@csrf_exempt
def search_igdb_games(request): #pragma: no cover
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
            # print(data)
            username = request.user.username  # Get the current user's username

            # Prepare the item to be saved in DynamoDB
            item = {
                'listId': str(uuid.uuid4()),
                'username': username,
                'name': data['name'][0],
                'description': data['description'][0],
                'visibility': data['visibility'][0],
                'games': data['games[]']
            }
            g = []
            for games in item['games']:
                gids = games.split(',')
                g.extend(gids)
            
            item['games'] = g
            
            try:
                table.put_item(Item=item)
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'failedToPutToDynamo'})


            return JsonResponse({'status': 'success'})
        
        except Exception as e:
            return JsonResponse({"status": "error"})

@login_required
def view_lists(request):
    return render(request, 'view_lists.html')


@login_required
def get_lists(request):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('lists')
    tab = request.GET.get('tab', 'my')
    
    page = int(request.GET.get('page', 1))
    page_size = 10

    if tab == 'my':
        filter_expression = Attr('username').eq(request.user.username)
    elif tab == 'discover':
        filter_expression = Attr('visibility').eq('public')


    response = table.scan(
        FilterExpression=filter_expression,
        Limit=page_size,
    )
    # TODO: Need to fix pagination!
    
    lists = response.get('Items', [])
    has_more = 'LastEvaluatedKey' in response

    data = {
        'lists': [
            {
                'name': item['name'],
                'description': item['description'],
                'creator': item['username'],
                'games_count': len(item['games'])
            }
            for item in lists
        ],
        'has_more': has_more
    }
    
    return JsonResponse(data)
