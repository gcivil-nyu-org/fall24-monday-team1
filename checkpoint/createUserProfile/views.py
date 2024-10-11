from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userProfile.models import UserProfile
from django.contrib.auth import get_user_model

@login_required
def create_profile(request):
    User = get_user_model()
    if request.method == 'POST':
        display_name = request.POST.get('display_name')
        bio = request.POST.get('bio')
        account_role = request.POST.get('account_role')
        privacy_setting = request.POST.get('privacy_setting')

        # Check if a profile already exists
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('userProfile:editProfile')

        profile = UserProfile.objects.create(
            user=request.user,
            display_name=display_name,
            bio=bio,
            account_role=account_role,
            privacy_setting=privacy_setting
        )
        profile.save()
        return redirect('userProfile:myProfile')  # Redirect to profile view

    return render(request, 'create_profile.html')
