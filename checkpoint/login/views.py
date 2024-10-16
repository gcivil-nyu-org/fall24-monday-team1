from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

def send_welcome_email(user):
    subject = 'Welcome to Checkpoint!'
    recipient_list = [user.email]

    # Render the HTML template
    html_content = render_to_string('checkpoint/userProfile/templates/welcome_email.html', {'user': user})
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, 'from@example.com', recipient_list)
    email.attach_alternative(html_content, 'text/html')
    email.send()

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
            messages.error(request, err)
            return redirect('signup')

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()

        # Send welcome email
        send_welcome_email(user)

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
            messages.success(request, "Login successful! Redirecting to your profile.")
            if UserProfile.objects.filter(user=request.user).exists():
                return redirect('userProfile:myProfile')  # Redirect to profile page
            else:
                return redirect('createUserProfile:createProfile')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect("/")

def home(request):
    return render(request, 'index.html')
