from django.urls import path
from .views.viewProfile import viewProfile, viewMyProfile, fetch_game_details
from .views.editProfile import editProfile
from .views.searchProfile import user_profile_list

app_name = 'userProfile'

urlpatterns = [
    path('view/<int:user_id>/', viewProfile, name='viewProfile'),
    path('myProfile/', viewMyProfile, name='myProfile'),
    path('edit/', editProfile, name='editProfile'),
    path('search/', user_profile_list, name='searchProfile'),
    path('fetch-game-details/', fetch_game_details, name='fetch_game_details'),
]