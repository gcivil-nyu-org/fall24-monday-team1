from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile
import boto3
import os

User = get_user_model()

class EventViewsTest(TestCase):

    def setUp(self):
        # Create a user and a user profile
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@events.com')
        self.user_profile = UserProfile.objects.create(user=self.user, account_role='event_organizer')

        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        self.table = self.dynamodb.Table('Events')  # Replace with your DynamoDB table name

    def tearDown(self):
        # Clear the Events table after each test
        self.table.delete_item(Key={'creator': self.user.id})  # Adjust according to your table's primary key schema

    def create_event(self, title, description, start_time, end_time, location):
        event = {
            'title': title,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'location': location,
            'creator': self.user.id  # Store creator as user ID
        }
        self.table.put_item(Item=event)

    def test_create_event_view_redirects_when_logged_in(self):
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
        response = self.table.scan()
        self.assertEqual(len(response['Items']), 1)
        self.assertEqual(response['Items'][0]['title'], 'Test Event')

    def test_create_event_view_forbidden_for_non_event_organizers(self):
        # Create a user with a different role
        non_organizer_user = User.objects.create_user(username='non_org_user', password='password')
        UserProfile.objects.create(user=non_organizer_user, account_role='viewer')

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
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Location 1'
        )
        self.create_event(
            title='Event 2',
            description='Description 2',
            start_time='2024-10-31 13:00',
            end_time='2024-10-31 15:00',
            location='Location 2'
        )

        response = self.client.get(reverse('events:event_list'))

        # Check that the response is successful and contains the events
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Event 1')
        self.assertContains(response, 'Event 2')
        self.assertTemplateUsed(response, 'events/event_list.html')

    def test_event_list_pagination(self):
        self.client.login(username='testuser', password='password')
        # Create 30 events for pagination testing
        for i in range(30):
            self.create_event(
                title=f'Event {i + 1}',
                description='Description',
                start_time='2024-10-31 10:00',
                end_time='2024-10-31 12:00',
                location='Location'
            )

        # Get the sixth page of events
        response = self.client.get(reverse('events:event_list') + '?page=6')

        if response.context['page_obj'].object_list:
            first_event_title = response.context['page_obj'].object_list[0]['title']
            last_event_title = response.context['page_obj'].object_list[-1]['title']
            
            print("First event on page 6:", first_event_title)
            print("Last event on page 6:", last_event_title)

            # Assert the titles
            self.assertEqual(first_event_title, 'Event 26')  
            self.assertEqual(last_event_title, 'Event 30')