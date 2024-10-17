from django.shortcuts import render
from django.http import HttpResponseRedirect
# import requests
# import os

def search_game(request):
    if request.method == 'POST':
        game_query = request.POST.get('game_query')
        print(game_query)
        # Here you can call IGDB API using the game_query
        # You can redirect to the results page or return the data
        # return HttpResponseRedirect('/results/')
    return render(request, 'search.html')