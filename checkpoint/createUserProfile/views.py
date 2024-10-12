from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userProfile.models import UserProfile
from .forms import UserProfileForm  # Import the form
from django.contrib import messages

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a profile already exists
            if UserProfile.objects.filter(user=request.user).exists():
                return redirect('userProfile:myProfile')
            
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('userProfile:myProfile')  # Redirect to profile view
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm()

    return render(request, 'create_profile.html', {'form': form})
