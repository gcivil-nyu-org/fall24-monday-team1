from django.urls import path
from . import views


app_name="gamesearch"
urlpatterns = [
    path('', views.search_game, name='search_game'), 
    path('game/<str:game_id>/', views.game_details_view, name='game-details'),
    path('game/<str:game_id>/fetch-data/', views.game_data_fetch_view, name='game-data-fetch'),
    path('save_to_shelf/', views.save_to_shelf, name='save_to_shelf'),
]
