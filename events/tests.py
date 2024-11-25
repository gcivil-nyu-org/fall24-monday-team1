from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile
import boto3
import os
from botocore.exceptions import ClientError
from .models import Event
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.text import slugify
import requests
import glob

User = get_user_model()


def create_table_if_not_exists(dynamodb):
    table_name = 'Events'  

    # Check if the table exists
    existing_tables = dynamodb.tables.all()
    if table_name in [table.name for table in existing_tables]:
        print(f"Table '{table_name}' already exists.")
        return

    # Create the table
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'eventId',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'eventId',
                    'AttributeType': 'S'  # String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully!")
    except ClientError as e:
        print(f"Failed to create table: {e.response['Error']['Message']}")

class EventViewsTest(TestCase):

    def setUp(self):
        # Create a user and a user profile
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@events.com')
        self.user_profile = UserProfile.objects.create(user=self.user, account_role='event_organizer')
        username = self.user.username
        avatar_url = f"https://ui-avatars.com/api/?name={username}"

        response = requests.get(avatar_url)
        if response.status_code == 200:
            # Create a unique filename for the image
            filename = f"{slugify(username)}.png"   
            # Save the image to the ImageField
            self.user_profile.profile_photo.save(filename, ContentFile(response.content), save=True)
        else:
            raise ValueError("Avatar link not available")
        # Create a user with a different role
        self.non_organizer_user = User.objects.create_user(username='non_org_user', password='password')
        UserProfile.objects.create(user=self.non_organizer_user, account_role='viewer')

        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        create_table_if_not_exists(self.dynamodb)
        self.table = self.dynamodb.Table('Events')  # Replace with your DynamoDB table name

    def tearDown(self):
        response = self.table.scan()  # Scan to get all items
        for item in response.get('Items', []):
            try:
            # Assuming 'creator' is the user ID
                creator_user = User.objects.get(id=int(item['creator']))
                print(f"Get user with name {creator_user.username}")
                if creator_user.username == 'testuser':  # Check if the item was created by the test user
                    self.table.delete_item(Key={'eventId': item['eventId']})  # Use the correct key schema
            except User.DoesNotExist:
                print(f"User not found {item['creator']} might because of the test case use different table")
                # self.table.delete_item(Key={'eventId': item['eventId']})  # Use the correct key schema
        media_directory = './media/profile_photos'  # Update this path

        # Construct the pattern for matching files
        pattern = os.path.join(media_directory, 'testuser*.png')

        # Use glob to find all files that match the pattern
        files_to_delete = glob.glob(pattern)

        # Delete the matched files
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
            
    def create_event(self, title, description, start_time, end_time, location, creator_id, participants=None):
        event = Event(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            creator=creator_id,
            participants=participants or []
        )
        event.save()
        return event

    def test_create_event_view_redirects_when_logged_in(self):
        # original_len = len(self.table.scan())
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('events:create_event'), {
            'title': 'Test Event',
            'description': 'A test event description.',
            'start_time': '2024-10-31 10:00',
            'end_time': '2024-10-31 12:00',
            'location': 'Test Location',
        })

        # Check that the event was created and redirected to the event list
        self.assertRedirects(response, reverse('events:event_list'))

        # Assert that the event exists in DynamoDB
        response = self.client.get(reverse('events:event_list'))
        # self.assertEqual(len(response['Items']), original_len + 1)
        self.assertContains(response, 'Test Event')

    def test_create_event_view_forbidden_for_non_event_organizers(self):
        self.client.login(username='non_org_user', password='password')
        response = self.client.get(reverse('events:create_event'))

        # Check that a 302 redirect is raised
        self.assertEqual(response.status_code, 302)

    def test_event_list_view(self):
        self.client.login(username='testuser', password='password')

        # Create a couple of events
        self.create_event(
            title='Event 1',
            description='Description 1',
            start_time='2000-10-31 10:00',
            end_time='2000-10-31 12:00',
            location='Location 1',
            creator_id=self.user.id,
        )
        self.create_event(
            title='Event 2',
            description='Description 2',
            start_time='2000-10-31 13:00',
            end_time='2000-10-31 15:00',
            location='Location 2',
            creator_id=self.user.id
        )

        response = self.client.get(reverse('events:event_list'))

        # Check that the response is successful and contains the events
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Event 1')
        self.assertContains(response, 'Event 2')
        self.assertTemplateUsed(response, 'events/event_list.html')

    def test_event_list_pagination_with_incremented_times(self):
        self.client.login(username='testuser', password='password')
        
        # Create 30 events with incremented start and end times
        for i in range(30):
            start_time = f'2024-10-31 {10 + (i // 5)}:0{i % 5}0:00'  # Increment minutes for diversity
            end_time = f'2024-10-31 {12 + (i // 5)}:0{i % 5}0:00'    # Increment minutes accordingly
            self.create_event(
                title=f'Event {i + 1}',
                description='Description',
                start_time=start_time,
                end_time=end_time,
                location='Location',
                creator_id=self.user.id
            )

        # Get the sixth page of events
        response = self.client.get(reverse('events:event_list') + '?page=6')
        
        # Check if the page object is populated
        self.assertTrue(response.context['page_obj'].object_list)

        # Assert the first and last event titles on page 6
        first_event_start_time = response.context['page_obj'].object_list[0]['start_time']
        last_event_start_time = response.context['page_obj'].object_list[-1]['start_time']
        
        print("First event on page 6:", first_event_start_time)
        print("Last event on page 6:", last_event_start_time)

        # Assertions for page 6
        # self.assertEqual(first_event_start_time, '2024-10-31 15:000:00')  # First event should be Event 26
        # self.assertEqual(last_event_start_time, '2024-10-31 15:040:00')   # Last event should be Event 30
        
        # Get the first page of events
        response = self.client.get(reverse('events:event_list') + '?page=1')

        # Check if the page object is populated
        self.assertTrue(response.context['page_obj'].object_list)

        # Assert the first and last event titles on page 1
        first_event_start_time = response.context['page_obj'].object_list[0]['start_time']
        last_event_start_time = response.context['page_obj'].object_list[-1]['start_time']
        
        print("First event on page 1:", first_event_start_time)
        print("Last event on page 1:", last_event_start_time)

        # Assertions for page 1
        # self.assertEqual(first_event_start_time, '2024-10-31 10:000:00')    # First event should be Event 1
        # self.assertEqual(last_event_start_time, '2024-10-31 10:040:00')     # Last event should be Event 5
    def get_event_from_dynamodb(self, event_id):
        response = self.table.get_item(Key={'eventId': event_id})
        return response.get('Item')

    def test_register_event_success(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id
        )

        response = self.client.post(reverse('events:register_event', args=[event.eventId]))

        # Check that the user is registered
        registered_event = self.get_event_from_dynamodb(event.eventId)
        self.assertIn(self.user.id, registered_event['participants'])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_detail', args=[event.eventId]))
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "You have successfully registered for the event.")

    def test_register_event_already_registered(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id,
            participants=[self.user.id]
        )

        response = self.client.post(reverse('events:register_event', args=[event.eventId]))

        # Check that the user is still registered
        registered_event = self.get_event_from_dynamodb(event.eventId)
        self.assertIn(self.user.id, registered_event['participants'])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_detail', args=[event.eventId]))
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "You are already registered for this event.")

    def test_register_event_not_found(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('events:register_event', args=[999]))  # Assuming 999 does not exist

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_list'))
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "Event not found.")

    def test_unregister_event_success(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id,
            participants=[self.user.id]
        )

        response = self.client.post(reverse('events:unregister_event', args=[event.eventId]))

        # Check that the user is unregistered
        registered_event = self.get_event_from_dynamodb(event.eventId)
        self.assertNotIn(self.user.id, registered_event['participants'])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_detail', args=[event.eventId]))
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "You have successfully unregistered from the event.")

    def test_unregister_event_not_registered(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id
        )

        response = self.client.post(reverse('events:unregister_event', args=[event.eventId]))

        # Check that the user is still not registered
        registered_event = self.get_event_from_dynamodb(event.eventId)
        self.assertNotIn(self.user.id, registered_event['participants'])
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_detail', args=[event.eventId]))
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "You are not registered for this event.")

    def test_event_detail_view(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id
        )

        response = self.client.get(reverse('events:event_detail', args=[event.eventId]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')
        self.assertTemplateUsed(response, 'events/event_detail.html')
        
    def test_edit_event_success(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id
        )

        response = self.client.post(reverse('events:edit_event', args=[event.eventId]), {
            'title': 'Updated Event',
            'description': 'Updated description.',
            'start_time': '2024-11-01 10:00',
            'end_time': '2024-11-01 12:00',
            'location': 'Updated Location'
        })

        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_detail', args=[event.eventId]))
        
        event = self.get_event_from_dynamodb(event.eventId)
        self.assertEqual(event['title'], 'Updated Event')
        self.assertEqual(event['description'], 'Updated description.')
        self.assertEqual(event['start_time'], '2024-11-01 10:00')
        self.assertEqual(event['end_time'], '2024-11-01 12:00')
        self.assertEqual(event['location'], 'Updated Location')

    def test_delete_event_success(self):
        self.client.login(username='testuser', password='password')
        event = self.create_event(
            title='Test Event',
            description='A test event description.',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Test Location',
            creator_id=self.user.id
        )

        response = self.client.post(reverse('events:delete_event', args=[event.eventId]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('events:event_list'))
        self.assertIsNone(self.get_event_from_dynamodb(event.eventId))  # Ensure the event is deleted
        self.assertEqual(list(messages.get_messages(response.wsgi_request))[0].message, "Event deleted successfully.")