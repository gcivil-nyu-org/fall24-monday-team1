from django.shortcuts import render
from django.http import JsonResponse

from django.urls import reverse
import requests
import os
from datetime import datetime
import boto3


from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from botocore.exceptions import ClientError

from boto3.dynamodb.conditions import Attr


def authorize_igdb():
        url = "https://id.twitch.tv/oauth2/token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (os.environ['igdb_client_id'], os.environ['igdb_client_secret'])
        return requests.request("POST", url, headers={}, data={})

@login_required
def search_game(request):
    if request.method == 'POST':
        game_query = request.POST.get('game_query')
        auth = authorize_igdb()
        

        url = "https://api.igdb.com/v4/games"
        
        payload = "search \"%s\"; fields name, first_release_date, cover, genres;\n" % (game_query)
        headers = {
        'Client-ID': os.environ.get("igdb_client_id"),
        'Authorization': f'Bearer {auth.json()["access_token"]}',
        'Content-Type': 'text/plain',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            search_result = response.json()
        else:
            search_result = []
        # print(search_result)
        # clean data
        data = []
        # 1. get actual cover image URL
        for game in search_result:
            row = {}
            row['id'] = game['id']
            img_url = None
            if 'name' in game:
                row['name'] = game['name']
            else:
                continue

            if 'cover' in game:
                try:
                    url = "https://api.igdb.com/v4/covers"
                    payload = "fields url; where id=%d;" % (game['cover'])
                    response = requests.request("POST", url, headers=headers, data=payload)
                    img_url = response.json()[0]["url"].split("//")[1]
                except Exception as e:
                    print(e)
                    pass
            row["img_url"] = img_url
                
        # 2. convert epoch to human readable form
        
            if 'first_release_date' in game:
                row['release_date'] = datetime.fromtimestamp(game['first_release_date']).strftime("%Y-%m-%d")
            else:
                row['release_date'] = None

            data.append(row)

        
        return render(request, 'search_result.html', {'games': data})
 
    return render(request, 'search.html')


def game_details_view(request, game_id):
    # print(request.GET.get('shelf'), request.GET.get('own'))
    # TODO: make a dynamoDB request instead to see if current user has this in completed shelf
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
    
        table = dynamodb.Table('user-shelves')
        filter_expression = Attr('user_id').eq(request.user.username)
        scan_params = {
        'FilterExpression': filter_expression,
        }
        response = table.scan(**scan_params)
        showReviewBox = False
        if response['Items']:
            completed_games = response['Items'][0]['completed']
            showReviewBox = str(game_id) in completed_games
        return render(request, 'game_details.html', {'game_id': game_id, 'showReviewBox': showReviewBox ,'curPath' : reverse('gamesearch:game-details', args=[game_id])})
    except Exception as e:
        print(e)
        return render(request, 'game_details.html', {'game_id': game_id, 'curPath' : reverse('gamesearch:game-details', args=[game_id])})
    

def game_data_fetch_view(request, game_id):
    auth = authorize_igdb()
        

    url = "https://api.igdb.com/v4/games"
    
    payload = "fields cover, genres, platforms, name, rating, first_release_date, summary, url; where id=%s;" % game_id
    headers = {
    'Client-ID': os.environ.get("igdb_client_id"),
    'Authorization': f'Bearer {auth.json()["access_token"]}',
    'Content-Type': 'text/plain',
    }


    response = requests.request("POST", url, headers=headers, data=payload)
    data = {}
    # print(response.json())
    
    for key,value in response.json()[0].items():
        if key == 'genres' or key == 'platforms':
            data[key] = []
            for id in value:
                url = "https://api.igdb.com/v4/%s"%key
                payload = "fields name; where id=%d;"%id
                response = requests.request("POST", url, headers=headers, data=payload)
                data[key].append(response.json()[0]["name"])
        elif key == 'first_release_date':
            data['release_year'] = datetime.fromtimestamp(value).strftime("%Y")
        elif key == "cover":
            url = "https://api.igdb.com/v4/covers"
            payload = "fields url; where id=%d;" % (value)
            response = requests.request("POST", url, headers=headers, data=payload)
            data['cover'] = response.json()[0]["url"].split("//")[1]
        else:
            data[key] = value

    youtube_api_url = "https://youtube.googleapis.com/youtube/v3/search"
    params = {
        "q": f"{data['name']} game trailer",
        "key": os.getenv("YOUTUBE_API_KEY"),
        "part": "snippet",
        "type": "video",
        "maxResults": 1
    }
    
    data['trailer'] = ''
    try:
        response = requests.get(youtube_api_url, params=params)
        response_data = response.json()

        if "items" in response_data and len(response_data["items"]) > 0:
            video_id = response_data["items"][0]["id"]["videoId"]
            data['trailer'] = 'https://www.youtube.com/embed/%s' % video_id
        else:
            print("error fetching trailer")
    except Exception as e:
        print(f"Error fetching trailer: {e}")
    return JsonResponse(data)



@csrf_exempt  # Disable CSRF protection for testing; handle securely in production
@login_required  # Ensure the user is logged in
def save_to_shelf(request):
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    # Reference the DynamoDB table
    table = dynamodb.Table('user-shelves')

    if request.method == 'POST':
        try:
            username = request.user.username

            game_id = request.POST.get('game_id')
            shelf_name = request.POST.get('shelf_name')

            response = table.get_item(Key={'user_id': username})
            otherShelf = False
            if 'Item' in response:
                user_shelves = response['Item']
                if shelf_name in user_shelves and game_id in user_shelves[shelf_name]:
                    return JsonResponse({'status': 'alreadyExists'})
                for shelf in user_shelves:
                    if shelf!='user_id' and game_id in user_shelves[shelf]:
                        user_shelves[shelf].remove(game_id)
                        otherShelf = True
                        break
                
            else:
                user_shelves = {
                    'user_id': username,
                    'completed': [],
                    'playing': [],
                    'want-to-play': [],
                    'abandoned': [],
                    'paused': []
                }
            # print(user_shelves)
            user_shelves[shelf_name].append(game_id)
            response = table.put_item(Item=user_shelves)

            # print(response)
            
            if otherShelf:
                return JsonResponse({'status': 'movedShelf'})
            if response:
                return JsonResponse({'status': 'success'})
            # else:
            #     return JsonResponse({'status': 'error'}, status=500)    

        except ClientError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Something went wrong!'}, status=400)

