from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userProfile.models import UserProfile
from .forms import UserProfileForm
from django.contrib import messages
from django.core.mail import send_mail
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
            for platform, username in zip(platforms, usernames):
                if platform and username:
                    gaming_usernames[platform] = username

            # Store the gaming usernames as a JSON field
            profile.gaming_usernames = json.dumps(gaming_usernames)  # Serialize to JSON
            profile.save()

            messages.success(request, 'Profile created successfully!')

            # Sending welcome email
            my_subject = "Welcome to Checkpoint!"
            my_message = (
    f"Dear {request.user.username},\n\n Welcome to Checkpoint! Thank you for signing up; we’re thrilled to have you as part of our community. "
    "Your journey starts here, and we encourage you to explore our features, connect with other users in our forums, and reach out to our support team at checkpointgame11@gmail.com if you have any questions. "
    "We’re excited to support you along the way, so be sure to complete your profile to personalize your experience. Thanks again for joining us!\n\n"
    "Best regards,\n"
    "The Checkpoint Team\n"
)
            my_recipient = request.user.email  # Get the email of the logged-in user
            
            try:
                send_mail(
                    subject=my_subject,
                    message=my_message,
                    from_email=None,
                    recipient_list=[my_recipient],
                    fail_silently=False
                )
                messages.info(request, 'A welcome email has been sent to your registered email.')
            except Exception as e:
                messages.error(request, f'Error sending email: {e}')

            return redirect('userProfile:myProfile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm()

    return render(request, 'create_profile.html', {'form': form})
