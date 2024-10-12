from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile


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
    
        if password1!=password2:
            messages.error(request, "Passwords don't match.")
            return redirect('signup')
    
        #TODO: add more password validations
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()

        messages.success(request, "New user added!")
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
            # if profile exists, redirect to create my profile, else to viewmyprofile
            if UserProfile.objects.filter(user=request.user).exists():
                return redirect('userProfile:myProfile')  # Redirect to profile page
            else:
                return redirect('createUserProfile:createProfile')
        else:
            print(f"Failed login attempt for user {username}.")  # Print message to console
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def home(request):
    return render(request, 'index.html')