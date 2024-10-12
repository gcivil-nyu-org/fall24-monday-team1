from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..models import UserProfile
from django.core.files.storage import FileSystemStorage
import json

@login_required
def editProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    print(profile)

    if request.method == 'POST':
        post_params = request.POST
        
        # Print all parameters
        for key, value in post_params.items():
            print(f'{key}: {value}')
        profile.display_name = request.POST.get('display_name')
        profile.bio = request.POST.get('bio')
        profile.privacy_setting = request.POST.get('privacy_setting')
        profile.account_role = request.POST.get('account_role')
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        gaming_usernames = {}
        prevPlatform = ""
        for key, value in request.POST.items():
            if key.startswith('gaming_usernames[') and key.endswith(']'):
                index = key[17:-1]  # Extract platform name from the key
                if (index[:12] == "__platform__"):
                    prevPlatform = value
                else:
                    if (index[:12] == "__username__" ):
                        gaming_usernames[prevPlatform] = value
                    else:
                        gaming_usernames[index] = value  # Add to the dictionary
        profile.gaming_usernames = gaming_usernames
        profile.save()
        return redirect('/profile/')  # Redirect to the profile view

    context = {
        'profile': profile
    }
    
    return render(request, 'editProfile.html', context)