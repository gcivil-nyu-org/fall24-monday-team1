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
        profile.display_name = request.POST.get('display_name')
        profile.bio = request.POST.get('bio')
        profile.privacy_setting = request.POST.get('privacy_setting')
        profile.account_role = request.POST.get('account_role')
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        
        # Handle gaming usernames JSON
        gaming_usernames = request.POST.get('gaming_usernames')
        if gaming_usernames:
            try:
                profile.gaming_usernames = json.loads(gaming_usernames)
            except json.JSONDecodeError:
                profile.gaming_usernames = {}  # Fallback to empty dict on error
        
        profile.save()
        return redirect('/profile/')  # Redirect to the profile view

    context = {
        'profile': profile
    }
    
    return render(request, 'editProfile.html', context)