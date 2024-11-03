from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FriendRequest

@login_required
def send_friend_request(request, to_user):
    if request.method == 'POST':
        if FriendRequest.send_request(request.user.username, to_user):
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

@login_required
def pending_friend_requests(request):
    pending_requests = FriendRequest.get_pending_requests(request.user.username)
    return render(request, 'friends/pending_requests.html', {'requests': pending_requests})

@login_required
def accept_friend_request(request, from_user):
    if request.method == 'POST':
        if FriendRequest.accept_request(from_user, request.user.username):
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

@login_required
def reject_friend_request(request, from_user):
    if request.method == 'POST':
        if FriendRequest.reject_request(from_user, request.user.username):
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

@login_required
def friend_list(request):
    friends = FriendRequest.get_friends(request.user.username)
    return render(request, 'friends/friend_list.html', {'friends': friends})

@login_required
def friend_requests(request):
    received_requests = FriendRequest.get_pending_requests(request.user.username)
    sent_requests = FriendRequest.get_sent_requests(request.user.username)
    friends = FriendRequest.get_friends(request.user.username)
    return render(request, 'friends/friend_requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'friends': friends
    })