from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

import requests
import os
import json
from datetime import datetime
import time

def authorize_igdb():
        url = "https://id.twitch.tv/oauth2/token?client_id=%s&client_secret=%s&grant_type=client_credentials" % (os.environ['igdb_client_id'], os.environ['igdb_client_secret'])
        return requests.request("POST", url, headers={}, data={})

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
        
        search_result = response.json()
        
        print(search_result)
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
                except:
                    pass
            row["img_url"] = img_url
                
        # 2. convert epoch to human readable form
        
            if 'first_release_date' in game:
                row['release_date'] = datetime.fromtimestamp(game['first_release_date']).strftime("%Y-%m-%d")
            else:
                row['release_date'] = None
        # # 3. get actual genre strings
        #     url = "https://api.igdb.com/v4/genres"
        #     if 'genres' in game:
        #         row['genres'] = []
        #         for gid in game['genres']:
        #             payload = "fields name; where id=%d;"%gid
        #             response = requests.request("POST", url, headers=headers, data=payload)
        #             row['genres'].append(response.json()[0]["name"])


            data.append(row)

        print(data)
        return render(request, 'search_result.html', {'games': data})


        
    return render(request, 'search.html')


def game_details_view(request, game_id):
    return render(request, 'game_details.html', {'game_id': game_id})

def game_data_fetch_view(request, game_id):
    auth = authorize_igdb()
        

    url = "https://api.igdb.com/v4/games"
    
    payload = "fields cover, genres, platforms, name, rating, first_release_date, summary, url; where id=%d;" % game_id
    headers = {
    'Client-ID': os.environ.get("igdb_client_id"),
    'Authorization': f'Bearer {auth.json()["access_token"]}',
    'Content-Type': 'text/plain',
    }


    response = requests.request("POST", url, headers=headers, data=payload)
    data = {}
    print(response.json())
    
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
            print(payload)
            response = requests.request("POST", url, headers=headers, data=payload)
            data['cover'] = response.json()[0]["url"].split("//")[1]
        else:
            data[key] = value

    # You can return HTML or JSON depending on how you want to populate the data
    return JsonResponse(data)