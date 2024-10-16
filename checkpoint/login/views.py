from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # Basic validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
    
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return redirect('signup')
        
        try:
            validators.validate_password(password=password1)
        except ValidationError as err:
            messages.error(request, list(err))  # Convert to list for proper display
            return redirect('signup')

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()

        # Send welcome email
        send_mail(
            "Welcome to Checkpoint!",
            "Thank you for signing up! We're glad to have you.",
            "from@example.com",  # Replace with your actual "from" email
            [user.email],
            fail_silently=False,
        )

        messages.success(request, "New user added! Welcome email sent.")
        new_user = authenticate(request, username=username, password=password1)
        login(request, new_user)
        return redirect('createUserProfile:createProfile')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            print(f"User {username} logged in successfully.")  # Print message to console
            messages.success(request, "Login successful! Redirecting to your profile.")
            # If profile exists, redirect to view my profile, else to create my profile
            if UserProfile.objects.filter(user=request.user).exists():
                return redirect('userProfile:myProfile')  # Redirect to profile page
            else:
                return redirect('createUserProfile:createProfile')
        else:
            print(f"Failed login attempt for user {username}.")  # Print message to console
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect("/")

def home(request):
    return render(request, 'index.html')
