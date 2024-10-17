from django.shortcuts import render
from django.http import HttpResponseRedirect
import requests
import os
import json

def search_game(request):
    def authorize_igdb():
        url = f"https://id.twitch.tv/oauth2/token?client_id={os.environ.get("client_id")}&client_secret={os.environ.get("client_secret")}&grant_type=client_credentials"
        return requests.request("POST", url, headers={}, data={})

    if request.method == 'POST':
        game_query = request.POST.get('game_query')
        auth = authorize_igdb()
        

        url = "https://api.igdb.com/v4/games"

        payload = "search \"%s\"; fields *;\n" % (game_query)
        headers = {
        'Client-ID': os.environ.get("client_id"),
        'Authorization': f'Bearer {auth.json()["access_token"]}',
        'Content-Type': 'text/plain',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        search_result = response.json()
        return render(request, 'search_result.html', {'games': search_result})


        
    return render(request, 'search.html')