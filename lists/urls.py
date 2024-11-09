from django.urls import path
from . import views


app_name="lists"

urlpatterns = [
    path('create-list/', views.create_list, name='create_list'),
    path('search-igdb-games/', views.search_igdb_games, name='search_igdb_games'),
    path('save_list/', views.save_list, name='save_list'),
]