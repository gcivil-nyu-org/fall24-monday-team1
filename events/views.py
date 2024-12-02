import os
import boto3
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from userProfile.models import UserProfile
from .models import Event
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def create_event(request):
    try:
        # Check if the user has the required role
        user_profile = get_object_or_404(UserProfile, user=request.user, account_role__in=["event_organizer", "creator"])
    except Http404:
        messages.error(request, "You must be a creator or event organizer to create an event")
        return redirect('events:event_list')

    if request.method == 'POST':
        # Retrieve data from the request
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location')

        # Create the event instance
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            creator=request.user.id  # Store creator as user ID
        )
        event.save()  # Save to DynamoDB

        print("Event created")
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

def get_event(event_id):
    """Fetch a single event by its ID."""
    events = get_all_events()
    for event in events:
        if event['eventId'] == event_id:
            return event
    return None

def event_list(request):
    list(messages.get_messages(request))

    events = get_all_events()
    
    # Sort events by start_time (or any other attribute)
    sorted_events = sorted(events, key=lambda x: x['start_time'])
    for event in sorted_events:
        try:
            # Assuming 'creator' is the user ID
            event['creator_user'] = User.objects.get(id=int(event['creator']))
        except User.DoesNotExist:
            event['creator_user'] = {}
            event['creator_user']["username"] = f"Can't find user with id {int(event['creator'])} with type int"
            
    # Setup pagination
    paginator = Paginator(sorted_events, 6)  # Show 5 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    return render(request, 'events/event_list.html', {'page_obj': page_obj, "loginIn": request.user.is_authenticated})


@login_required
def register_event(request, event_id):
    """Register the logged-in user for an event."""
    event = get_event(event_id)
    if not event:
        messages.error(request, "Event not found.")
        return redirect('events:event_list')

    if request.user.id in event.get('participants', []):
        messages.warning(request, "You are already registered for this event.")
    else:
        event['participants'].append(request.user.id)  # Add user as participant
        messages.success(request, "You have successfully registered for the event.")

        # Save changes to DynamoDB
        event_obj = Event(
            title=event['title'],
            description=event['description'],
            start_time=event['start_time'],
            end_time=event['end_time'],
            location=event['location'],
            creator=event['creator'],
            participants=event['participants'],
            event_id=event['eventId']  # Pass the existing event ID
        )
        event_obj.save()  # Save updated event to DynamoDB

    return redirect('events:event_detail', event_id=event_id)

@login_required
def unregister_event(request, event_id):
    """Unregister the logged-in user from an event."""
    event = get_event(event_id)
    if not event:
        messages.error(request, "Event not found.")
        return redirect('events:event_list')

    if request.user.id not in event.get('participants', []):
        messages.warning(request, "You are not registered for this event.")
    else:
        event['participants'].remove(request.user.id)  # Remove user from participants
        messages.success(request, "You have successfully unregistered from the event.")

        # Save changes to DynamoDB
        event_obj = Event(
            title=event['title'],
            description=event['description'],
            start_time=event['start_time'],
            end_time=event['end_time'],
            location=event['location'],
            creator=event['creator'],
            participants=event['participants'],
            event_id=event['eventId']  # Pass the existing event ID
        )
        event_obj.save()  # Save updated event to DynamoDB

    return redirect('events:event_detail', event_id=event_id)

def event_detail(request, event_id):
    """View for displaying event details."""
    event = get_event(event_id)  # Fetch the event details

    if not event:
        messages.error(request, "Event not found.")
        return redirect('events:event_list')

    # Populate creator user
    try:
        event['creator_user'] = User.objects.get(id=int(event['creator']))
    except User.DoesNotExist:
        event['creator_user'] = {}
        event['creator_user']["username"] = f"Can't find user with id {int(event['creator'])}"

    # Populate participants
    event['participants_users'] = []
    is_participant = False
    for participant_id in event.get('participants', []):
        try:
            user = User.objects.get(id=int(participant_id))
            if (int(participant_id) == int(request.user.pk)):
                is_participant = True
            event['participants_users'].append(user)
        except User.DoesNotExist:
            event['participants_users'].append({
                "username": f"Can't find user with id {int(participant_id)}"
            })

    context = {
        'event': event,
        'is_participant': is_participant,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def edit_event(request, event_id):
    # Retrieve the event using the provided function
    event = get_event(event_id)
    print(event)
    print(event_id)

    # Check if the event exists
    if event is None:
        messages.error(request, "Event not found.")
        return redirect('events:event_list')

    # Check if the current user is the creator of the event
    if event['creator'] != request.user.id:
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('events:event_detail', event_id=event_id)

    if request.method == 'POST':
        # Retrieve data from the request
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location')

        # Update the event instance in DynamoDB
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        table = dynamodb.Table('Events')
        table.update_item(
            Key={'eventId': event_id},
            UpdateExpression="set title=:t, description=:d, start_time=:st, end_time=:et, #l=:l",
            ExpressionAttributeValues={
                ':t': title,
                ':d': description,
                ':st': start_time,
                ':et': end_time,
                ':l': location
            },
            ExpressionAttributeNames={
                "#l": "location"
            }
        )

        messages.success(request, "Event updated successfully.")
        return redirect('events:event_detail', event_id=event_id)  # Redirect to the event list view

    # Render the edit event template with the existing event data
    return render(request, 'events/edit_event.html', {
        "event": event,
        "loginIn": request.user.is_authenticated
    })


@login_required
def delete_event(request, event_id):
    # Retrieve the event using the provided function
    event = get_event(event_id)

    # Check if the event exists
    if event is None:
        messages.error(request, "Event not found.")
        return redirect('events:event_list')

    # Check if the current user is the creator of the event
    try:
        if event['creator'] != request.user.id:
            messages.error(request, "You do not have permission to delete this event.")
            return redirect('events:event_list')
    except Exception:
        pass     

    # Delete the event from DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('Events')
    table.delete_item(Key={'eventId': event_id})

    messages.success(request, "Event deleted successfully.")
    return redirect('events:event_list')  # Redirect to the event list view

@login_required
def my_events(request):
    """View for displaying events the logged-in user is registered for."""
    events = get_all_events()  # Fetch all events
    my_events = []

    # Filter for events where the user is a participant
    for event in events:
        if request.user.id in event.get('participants', []):
            my_events.append(event)

    # Sort my_events by start_time (or any other attribute)
    sorted_my_events = sorted(my_events, key=lambda x: x['start_time'])

    context = {
        'my_events': sorted_my_events,
        'loginIn': request.user.is_authenticated,
    }
    return render(request, 'events/my_events.html', context)