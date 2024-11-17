from django.urls import path
from .views import create_event, event_list, register_event, unregister_event, event_detail

app_name="events"
urlpatterns = [
    path('create/', create_event, name='create_event'),  # URL for creating an event
    path('events/register/<str:event_id>/', register_event, name='register_event'),  # URL for registering for an event
    path('events/unregister/<str:event_id>/', unregister_event, name='unregister_event'),  # URL for unregistering from an event
    path('events/<str:event_id>/', event_detail, name='event_detail'),  # URL for viewing event details
    path('', event_list, name='event_list'),  # URL for listing events
]