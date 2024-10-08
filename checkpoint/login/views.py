from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model


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
    
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.save()

        messages.success(request, "New user added!")
        # TODO: redirect to profile page

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # TODO: redirect to dashboard/profile page
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'index.html')