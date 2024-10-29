from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from .models import UserProfile
from .forms import UserProfileForm
import json

class UserProfileTests(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.client.login(username='testuser', password='password')

    def test_profile_creation_with_valid_data(self):
        # Define the URL for the profile creation view
        url = reverse('profile_create')  # Replace with your actual URL name if different

        # Define POST data
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'platforms[]': ['PlayStation', 'Xbox'],
            'gaming_usernames[]': ['john_doe_ps', 'john_doe_xbox'],
        }

        # Send POST request to create a profile
        response = self.client.post(url, data=post_data)

        # Check that a new UserProfile was created
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        
        # Verify that the gaming usernames were stored as JSON
        profile = UserProfile.objects.get(user=self.user)
        gaming_usernames = json.loads(profile.gaming_usernames)
        self.assertEqual(gaming_usernames['PlayStation'], 'john_doe_ps')
        self.assertEqual(gaming_usernames['Xbox'], 'john_doe_xbox')

        # Verify that the response redirected to the profile page
        self.assertRedirects(response, reverse('userProfile:myProfile'))

        # Verify that a welcome email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Welcome to Checkpoint!', mail.outbox[0].subject)
        self.assertIn('Dear testuser,', mail.outbox[0].body)

        # Check the success message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Profile created successfully!" in str(message) for message in messages))

    def test_duplicate_profile_prevention(self):
        # Create an existing UserProfile for the user
        UserProfile.objects.create(user=self.user)

        # Define the URL for the profile creation view
        url = reverse('profile_create')  # Replace with your actual URL name if different

        # Define POST data
        post_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'platforms[]': ['PlayStation', 'Xbox'],
            'gaming_usernames[]': ['john_doe_ps', 'john_doe_xbox'],
        }

        # Send POST request to create a profile
        response = self.client.post(url, data=post_data)

        # Verify that no additional UserProfile was created
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)

        # Verify that the response redirected to the profile page
        self.assertRedirects(response, reverse('userProfile:myProfile'))

        # Check for any messages indicating profile already exists or redirection
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("You already have a profile!" in str(message) for message in messages))
        
        # Ensure no welcome email was sent
        self.assertEqual(len(mail.outbox), 0)


