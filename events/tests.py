from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from userProfile.models import UserProfile
from .models import Event
User = get_user_model()

class EventViewsTest(TestCase):

    def setUp(self):
        # Create a user and a user profile
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@events.com')
        self.user_profile = UserProfile.objects.create(user=self.user, account_role='event_organizer')

    def tearDown(self):
        # Optionally delete objects created in setUp if needed
        self.user.delete()
        self.user_profile.delete()

    def test_create_event_view_redirects_when_logged_in(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('create_event'), {
            'title': 'Test Event',
            'description': 'A test event description.',
            'start_time': '2024-10-31 10:00',
            'end_time': '2024-10-31 12:00',
            'location': 'Test Location',
        })

        # Check that the event was created and redirected to the event list
        self.assertRedirects(response, reverse('events:event_list'))
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().title, 'Test Event')

    def test_create_event_view_forbidden_for_non_event_organizers(self):
        # Create a user with a different role
        non_organizer_user = User.objects.create_user(username='non_org_user', password='password')
        UserProfile.objects.create(user=non_organizer_user, account_role='viewer')

        self.client.login(username='non_org_user', password='password')
        response = self.client.get(reverse('create_event'))

        # Check that a 404 error is raised
        self.assertEqual(response.status_code, 404)

    def test_event_list_view(self):
        # Create a couple of events
        self.client.login(username='testuser', password='password')
        Event.objects.create(
            title='Event 1',
            description='Description 1',
            start_time='2024-10-31 10:00',
            end_time='2024-10-31 12:00',
            location='Location 1',
            creator=self.user
        )
        Event.objects.create(
            title='Event 2',
            description='Description 2',
            start_time='2024-10-31 13:00',
            end_time='2024-10-31 15:00',
            location='Location 2',
            creator=self.user
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
            Event.objects.create(
                title=f'Event {i + 1}',
                description='Description',
                start_time='2024-10-31 10:00',
                end_time='2024-10-31 12:00',
                location='Location',
                creator=self.user
            )

        # Get the sixth page of events
        response = self.client.get(reverse('events:event_list') + '?page=6')

        if response.context['page_obj'].object_list:
            first_event_title = response.context['page_obj'].object_list[0].title
            last_event_title = response.context['page_obj'].object_list[-1].title
            
            print("First event on page 6:", first_event_title)
            print("Last event on page 6:", last_event_title)

            # Assert the titles
            self.assertEqual(first_event_title, 'Event 26')  
            self.assertEqual(last_event_title, 'Event 30')   