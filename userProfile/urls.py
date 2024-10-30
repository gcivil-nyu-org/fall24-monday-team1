from django.urls import path
from . import views

app_name = "userProfile"
urlpatterns = [
    path('', views.viewMyProfile, name='myProfile'),
    path('view/<int:user_id>/', views.viewProfile, name='viewProfile'),
    path('edit/', views.editProfile, name="editProfile"),
    path('search/', views.UserProfileListView.as_view(), name="searchProfile"),
    path('fetch-game-details/', views.fetch_game_details, name='fetch_game_details'),
]