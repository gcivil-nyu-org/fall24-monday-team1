from django.urls import path
from . import views


app_name="lists"

urlpatterns = [
    path('create-list/', views.create_list, name='create_list'),
    path('search-igdb-games/', views.search_igdb_games, name='search_igdb_games'),
    path('save_list/', views.save_list, name='save_list'),
    path('', views.view_lists, name='view_lists'),
    path('get_lists/', views.get_lists, name='get_lists'),
    path('list-details/<list_id>/', views.fetch_list_details, name='fetch_list_details'),
    path('delete_list', views.delete_list, name='delete_list'),
    path('edit-list/<str:list_id>/', views.edit_list, name='edit_list'),
    path('update-list/', views.update_list, name='update_list'),
]