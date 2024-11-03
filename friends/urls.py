from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('requests/', views.friend_requests, name='friend_requests'),
    path('send-request/<str:to_user>/', views.send_friend_request, name='send_request'),
    path('pending-requests/', views.pending_friend_requests, name='pending_requests'),
    path('accept-request/<str:from_user>/', views.accept_friend_request, name='accept_request'),
    path('reject-request/<str:from_user>/', views.reject_friend_request, name='reject_request'),
    path('friend-list/', views.friend_list, name='friend_list'),
]