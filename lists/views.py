from django.shortcuts import render
import requests
from django.http import JsonResponse
import os
from gamesearch.views import authorize_igdb
from django.views.decorators.csrf import csrf_exempt

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