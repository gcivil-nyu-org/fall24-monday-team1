from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_game, name='search_game'), 
]