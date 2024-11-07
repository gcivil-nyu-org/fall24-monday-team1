import os
import boto3
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from userProfile.models import UserProfile
from .models import Event



@login_required
def create_event(request):
    try:
        # Check if the user has the required role
        user_profile = get_object_or_404(UserProfile, user=request.user, account_role__in=["event_organizer", "creator"])
    except Http404:
        messages.error(request, "You must be a creator or event organizer to create event")
        return redirect('events:event_list')
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
        return redirect('events:event_list')  # Redirect to the event list view

    return render(request, 'events/create_event.html', {"loginIn": request.user.is_authenticated})  # Render the static template for GET request

def get_all_events():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('Events')  # Replace with your DynamoDB table name
    response = table.scan()
    return response.get('Items', [])

def event_list(request):
    events = get_all_events()
    # Setup pagination
    paginator = Paginator(events, 5)  # Show 5 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {'page_obj': page_obj, "loginIn": request.user.is_authenticated})