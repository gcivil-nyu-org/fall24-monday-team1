from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from ..models import UserProfile

def viewProfile(request, user_id):
    # Retrieve the user profile based on the user_id
    profile = get_object_or_404(UserProfile, user__id=user_id)

    viewable = False

    if (profile.user == request.user):
        viewable = True
    if (profile.privacy_setting == "public"):
        viewable = True
    if (profile.privacy_setting == "friends_only"):
        pass
    
    # Prepare the context with the profile data
    context = {
        'profile': profile,
        'viewable': viewable,
        'gaming_usernames': profile.gaming_usernames,
        'own' : profile.user == request.user,
        'loginIn' : request.user.is_authenticated
    }

    return render(request, 'profileView.html', context)

@login_required
def viewMyProfile(request):
    return viewProfile(request, request.user.pk)