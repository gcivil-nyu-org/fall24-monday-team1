from django.urls import path
from .views import create_event, event_list, register_event, unregister_event, event_detail, \
    edit_event, delete_event, my_events

app_name="events"
urlpatterns = [
    path('create/', create_event, name='create_event'),  # URL for creating an event
    path('register/<str:event_id>/', register_event, name='register_event'),  # URL for registering for an event
    path('unregister/<str:event_id>/', unregister_event, name='unregister_event'),  # URL for unregistering from an event
    path('my-events/', my_events, name='my_events'),
    path('<str:event_id>/', event_detail, name='event_detail'),  # URL for viewing event details
    path('<str:event_id>/edit', edit_event, name='edit_event'),
    path('<str:event_id>/delete', delete_event, name='delete_event'),
    path('', event_list, name='event_list'),  # URL for listing events
]