from django.urls import path
from . import views

app_name = 'createUserProfile'

urlpatterns = [
    path('create/', views.create_profile, name='createProfile'),
]
