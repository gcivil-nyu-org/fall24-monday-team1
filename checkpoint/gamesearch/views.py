from django.shortcuts import render
from django.http import HttpResponseRedirect
import requests
import os
import json
from datetime import datetime

def search_game(request):
    def authorize_igdb():
        url = f"https://id.twitch.tv/oauth2/token?client_id={os.environ.get("client_id")}&client_secret={os.environ.get("client_secret")}&grant_type=client_credentials"

        return requests.request("POST", url, headers={}, data={})

    if request.method == 'POST':
        game_query = request.POST.get('game_query')
        auth = authorize_igdb()
        

        url = "https://api.igdb.com/v4/games"
        
        payload = "search \"%s\"; fields name, first_release_date, cover, genres;\n" % (game_query)
        headers = {
        'Client-ID': os.environ.get("client_id"),
        'Authorization': f'Bearer {auth.json()["access_token"]}',
        'Content-Type': 'text/plain',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        search_result = json.loads(response.text)
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
                url = "https://api.igdb.com/v4/covers"
                payload = "fields url; where id=%d;" % (game['cover'])
                response = requests.request("POST", url, headers=headers, data=payload)
                img_url = response.json()[0]["url"].split("//")[1]
            row["img_url"] = img_url
                
        # 2. convert epoch to human readable form
        
            if 'first_release_date' in game:
                row['release_date'] = datetime.fromtimestamp(game['first_release_date']).strftime("%Y-%m-%d")
            else:
                row['release_date'] = None
        # 3. get actual genre strings
            url = "https://api.igdb.com/v4/genres"
            if 'genres' in game:
                row['genres'] = []
                for gid in game['genres']:
                    payload = "fields name; where id=%d;"%gid
                    response = requests.request("POST", url, headers=headers, data=payload)
                    row['genres'].append(response.json()[0]["name"])


            data.append(row)

        print(data)
        return render(request, 'search_result.html', {'games': data})


        
    return render(request, 'search.html')