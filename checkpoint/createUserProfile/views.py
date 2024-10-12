from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userProfile.models import UserProfile
from .forms import UserProfileForm  # Import the form
from django.contrib import messages
import json

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        post_params = request.POST
        # Print all parameters
        if form.is_valid():

            # Check if a profile already exists
            if UserProfile.objects.filter(user=request.user).exists():
                return redirect('userProfile:myProfile')

            profile = form.save(commit=False)
            profile.user = request.user

            # Parse the gaming usernames from the POST data
            gaming_usernames = {}
            platforms = request.POST.getlist('platforms[]')  # Get list of platforms
            usernames = request.POST.getlist('gaming_usernames[]')  # Get list of usernames
            print(platforms)
            print(usernames)
            for platform, username in zip(platforms, usernames):
                if platform and username:
                    gaming_usernames[platform] = username

            # Store the gaming usernames as a JSON field
            profile.gaming_usernames = json.dumps(gaming_usernames)
            print(profile.gaming_usernames)
            profile.save()

            messages.success(request, 'Profile created successfully!')
            return redirect('userProfile:myProfile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm()

    return render(request, 'create_profile.html', {'form': form})
