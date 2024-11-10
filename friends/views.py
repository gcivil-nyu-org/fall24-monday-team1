from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import FriendRequest
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def pending_friend_requests(request):
    try:
        pending_requests = FriendRequest.get_pending_requests(request.user.username)
        return render(request, 'friends/friend_requests.html', {
            'received_requests': pending_requests,
            'sent_requests': [],
            'loginIn': True
        })
    except Exception as e:
        messages.error(request, f"Error loading friend requests: {str(e)}")
        return redirect('userProfile:myProfile')

@login_required
def friend_requests(request):
    try:
        # Get the current user's username
        username = request.user.username
        
        # Get requests
        received_requests = FriendRequest.get_pending_requests(username)
        sent_requests = FriendRequest.get_sent_requests(username)
        

        context = {
            'received_requests': received_requests,
            'sent_requests': sent_requests,
            'loginIn': True,
            'error_message': None
        }
        
        return render(request, 'friends/friend_requests.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading friend requests: {str(e)}")
        context = {
            'received_requests': [],
            'sent_requests': [],
            'loginIn': True,
            'error_message': str(e)
        }
        return render(request, 'friends/friend_requests.html', context)

@login_required
def send_friend_request(request, to_user):
    try:
        result = FriendRequest.send_request(request.user.username, to_user)
        print("Friend request data:", {  # Debug print
            'from_user': request.user.username,
            'to_user': to_user,
            'status': 'pending'
        })
        if result:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to send friend request'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def accept_friend_request(request, from_user):
    if request.method == 'POST':
        try:
            if FriendRequest.accept_request(from_user, request.user.username):
                messages.success(request, f'You are now friends with {from_user}!')
            else:
                messages.error(request, 'Failed to accept friend request.')
            return redirect('friends:friend_requests')
        except Exception as e:
            messages.error(request, f'Error accepting friend request: {str(e)}')
            return redirect('friends:friend_requests')

@login_required
def reject_friend_request(request, from_user):
    if request.method == 'POST':
        try:
            if FriendRequest.reject_request(from_user, request.user.username):
                messages.success(request, 'Friend request rejected.')
            else:
                messages.error(request, 'Failed to reject friend request.')
            return redirect('friends:friend_requests')
        except Exception as e:
            messages.error(request, f'Error rejecting friend request: {str(e)}')
            return redirect('friends:friend_requests')

@login_required
def friend_list(request):
    try:
        friends = FriendRequest.get_friends(request.user.username)
        return render(request, 'friends/friends_list.html', {
            'friends': friends,
            'loginIn': True
        })
    except Exception as e:
        messages.error(request, f"Error loading friends list: {str(e)}")
        return render(request, 'friends/friends_list.html', {
            'friends': [],
            'loginIn': True,
            'error_message': f"Error loading friends list: {str(e)}"
        })

@login_required
def cancel_friend_request(request, to_user):
    try:
        result = FriendRequest.reject_request(request.user.username, to_user)  # We can reuse reject_request method
        if result:
            messages.success(request, 'Friend request cancelled successfully.')
        else:
            messages.error(request, 'Failed to cancel friend request.')
        return redirect('friends:friend_requests')
    except Exception as e:
        messages.error(request, f'Error cancelling friend request: {str(e)}')
        return redirect('friends:friend_requests')

@login_required
def unfriend(request, friend_username):
    if request.method == 'POST':
        try:
            if FriendRequest.remove_friend(request.user.username, friend_username):
                messages.success(request, f'Removed {friend_username} from friends.')
            else:
                messages.error(request, 'Failed to remove friend.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})