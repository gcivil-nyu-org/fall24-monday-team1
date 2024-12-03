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
from datetime import datetime


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

@csrf_exempt
@login_required
def get_lists(request):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('lists')
    tab = request.POST.get('tab', 'my')
    
    # Filter based on tab type
    if tab == 'my':
        filter_expression = Attr('username').eq(request.user.username)
    elif tab == 'discover':
        filter_expression = Attr('visibility').eq('public') & Attr('username').ne(request.user.username)

    # Set up the parameters for scan
    scan_params = {
        'FilterExpression': filter_expression,
    }

    response = table.scan(**scan_params)
    lists = response.get('Items', [])
    
    data = {
        'lists': [
            {
                'id': item['listId'],
                'name': item['name'],
                'description': item['description'],
                'creator': item['username'],
                'games_count': len(item['games'])
            }
            for item in lists
        ],
        'has_more': 'LastEvaluatedKey' in response,
        'last_key': response.get('LastEvaluatedKey', {}).get('listId', None)
    }
    print("Sending data:", data)  # Add this for debugging
    return JsonResponse(data)

@csrf_exempt
def delete_list(request):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('lists')
    try:
        table.delete_item(Key={"listId" : request.POST.get('listID', '')})
        return JsonResponse({"message": "success", "details": "Successfully deleted list!"})
    except Exception as e:
        print(e)
        return JsonResponse({"message": "error", "details": "Failed to delete!"})
@login_required
def fetch_list_details(request, list_id):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('lists')

    # Fetch the list details from DynamoDB
    response = table.get_item(Key={'listId': list_id})
    list_details = response.get('Item', None)

    if not list_details:
        return render(request, 'list_not_found.html', status=404)

    # Check if user has permission to view the list
    is_owner = request.user.username == list_details.get('username')
    is_public = list_details.get('visibility') == 'public'

    if not (is_owner or is_public):
        return render(request, 'list_not_found.html', {
            'error_message': 'This list is private and cannot be viewed.'
        }, status=403)

    # If we get here, user has permission to view the list
    game_details = []
    game_ids = list_details.get('games', [])

    if game_ids:
        auth = authorize_igdb()
        headers = {
            'Client-ID': os.environ.get("igdb_client_id"),
            'Authorization': f'Bearer {auth.json()["access_token"]}',
            'Content-Type': 'text/plain',
        }

        payload = f"fields name, first_release_date, cover.url, summary; where id = ({','.join(game_ids)});"
        url = "https://api.igdb.com/v4/games"
        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            igdb_games = response.json()
            for game in igdb_games:
                game_detail = {
                    'id': game.get('id'),
                    'name': game.get('name'),
                    'summary': (game.get('summary', 'No description available')[:150] + '...') if len(game.get('summary', '')) > 150 else game.get('summary', 'No description available'),
                    'release_date': datetime.fromtimestamp(game['first_release_date']).strftime("%Y-%m-%d") if 'first_release_date' in game else 'Unknown',
                    'cover': game['cover']['url'].replace("//", "https://") if 'cover' in game else None
                }
                game_details.append(game_detail)

    return render(request, 'list_details.html', {
        'list': list_details,
        'game_details': game_details,
        'is_owner': is_owner
    })