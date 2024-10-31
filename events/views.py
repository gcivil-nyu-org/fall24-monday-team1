from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from userProfile.models import UserProfile
from .models import Event
from .forms import EventForm

@login_required
def create_event(request):
    # Check if the user has the required role
    user_profile = get_object_or_404(UserProfile, user=request.user, account_role__in=["event_organizer", "creator"])

    if request.method == 'POST':
        # Retrieve data from the request
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location')

        # Create the event instance
        Event.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            creator=request.user  # Set creator to the logged-in user
        )
        print("Event created: " + str(Event.objects.count()))
        return redirect('event_list')  # Redirect to the event list view

    return render(request, 'events/create_event.html', {"loginIn": request.user.is_authenticated})  # Render the static template for GET request

def event_list(request):
    events = Event.objects.all()

    # Setup pagination
    paginator = Paginator(events, 5)  # Show 5 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {'page_obj': page_obj, "loginIn": request.user.is_authenticated})