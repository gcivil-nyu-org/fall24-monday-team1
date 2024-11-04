from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import FriendRequest

@login_required
def pending_friend_requests(request):
    try:
        pending_requests = FriendRequest.get_pending_requests(request.user.username)
        return render(request, 'friends/friend_requests.html', {
            'received_requests': pending_requests
        })
    except Exception as e:
        messages.error(request, f"Error loading friend requests: {str(e)}")
        return redirect('userProfile:myProfile')

@login_required
def friend_requests(request):
    try:
        received_requests = FriendRequest.get_pending_requests(request.user.username)
        sent_requests = FriendRequest.get_sent_requests(request.user.username)
        print(received_requests)
        print(sent_requests)
        return render(request, 'friends/friend_requests.html', {
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'loginIn': True,
            'error_message': None
        })
    except Exception as e:
        return render(request, 'friends/friend_requests.html', {
            'received_requests': [],
            'sent_requests': [],
            'loginIn': True,
            'error_message': f"Error loading friend requests: {str(e)}"
        })

@login_required
def send_friend_request(request, to_user):
    if request.method == 'POST':
        try:
            if FriendRequest.send_request(request.user.username, to_user):
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Failed to send request'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def accept_friend_request(request, from_user):
    if request.method == 'POST':
        try:
            if FriendRequest.accept_request(from_user, request.user.username):
                messages.success(request, 'Friend request accepted!')
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Failed to accept request'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def reject_friend_request(request, from_user):
    if request.method == 'POST':
        try:
            if FriendRequest.reject_request(from_user, request.user.username):
                messages.success(request, 'Friend request rejected')
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Failed to reject request'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def friend_list(request):
    try:
        friends = FriendRequest.get_friends(request.user.username)
        return render(request, 'friends/friends_list.html', {
            'friends': friends,
            'loginIn': True
        })
    except Exception as e:
        return render(request, 'friends/friends_list.html', {
            'friends': [],
            'loginIn': True,
            'error_message': f"Error loading friends list: {str(e)}"
        })