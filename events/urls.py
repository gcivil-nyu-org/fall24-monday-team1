from django.urls import path
from .views import create_event, event_list

urlpatterns = [
    path('create/', create_event, name='create_event'),  # URL for creating an event
    path('', event_list, name='event_list'),  # URL for listing events
]