from django.test import TestCase
from django.urls import reverse
from django.core import mail
from userProfile.models import UserProfile
from .forms import UserProfileForm
import json
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileTests(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.client.login(username='testuser', password='password')

    def test_profile_creation_with_valid_data(self):
        # Define the URL for the profile creation view
        url = reverse('createUserProfile:createProfile')  # Replace with your actual URL name if different

        # Define POST data
        post_data = {
            'display_name': 'John',
            'bio': 'orihg',
            'privacy_setting': 'private',
            'account_role': 'gamer',
            'platforms[]': ['PlayStation', 'Xbox'],
            'gaming_usernames[]': ['john_doe_ps', 'john_doe_xbox'],
        }

        response = self.client.post(url, data=post_data)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        
        
        profile = UserProfile.objects.get(user=self.user)
        gaming_usernames = json.loads(profile.gaming_usernames)
        self.assertEqual(gaming_usernames['PlayStation'], 'john_doe_ps')
        self.assertEqual(gaming_usernames['Xbox'], 'john_doe_xbox')

        
        self.assertRedirects(response, reverse('userProfile:myProfile'))

        
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Welcome to Checkpoint!', mail.outbox[0].subject)
        self.assertIn('Dear testuser,', mail.outbox[0].body)


        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Profile created successfully!" in str(message) for message in messages))

    def test_duplicate_profile_prevention(self):
        # Create an existing UserProfile for the user
        UserProfile.objects.create(user=self.user)

        
        url = reverse('createUserProfile:createProfile')

        
        post_data = {
            'display_name': 'John',
            'bio': 'orihg',
            'privacy_setting': 'private',
            'account_role': 'gamer',
            'platforms[]': ['PlayStation', 'Xbox'],
            'gaming_usernames[]': ['john_doe_ps', 'john_doe_xbox'],
        }

        response = self.client.post(url, data=post_data)

        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)

        self.assertRedirects(response, reverse('userProfile:myProfile'))
    
    def test_invalid_form(self):
        UserProfile.objects.create(user=self.user)

        
        url = reverse('createUserProfile:createProfile')

        
        post_data = {
            
        }
        response = self.client.post(url, data=post_data)

        self.assertEqual(response.status_code, 200)
    
    def test_get_call(self):
        UserProfile.objects.create(user=self.user)

        
        url = reverse('createUserProfile:createProfile')

        
        post_data = {
            
        }
        response = self.client.get(url, data=post_data)

        self.assertEqual(response.status_code, 200)

    def test_get_call_no_profile(self):
        """Test GET request when user has no profile"""
        url = reverse('createUserProfile:createProfile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Should show create profile page
    
    def test_get_call_with_profile(self):
        """Test GET request when user already has a profile"""
        # Create a profile first
        UserProfile.objects.create(user=self.user)
        
        url = reverse('createUserProfile:createProfile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('userProfile:myProfile'))
    
    def test_invalid_form_no_profile(self):
        """Test POST with invalid form when user has no profile"""
        url = reverse('createUserProfile:createProfile')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 200)  # Should show form with errors
    
    def test_invalid_form_with_profile(self):
        """Test POST with invalid form when user already has profile"""
        # Create a profile first
        UserProfile.objects.create(user=self.user)
        
        url = reverse('createUserProfile:createProfile')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, reverse('userProfile:myProfile'))

    def test_duplicate_profile_prevention(self):
        """Test that users can't create multiple profiles"""
        # Create an existing UserProfile for the user
        UserProfile.objects.create(user=self.user)
        
        url = reverse('createUserProfile:createProfile')
        post_data = {
            'display_name': 'John',
            'bio': 'orihg',
            'privacy_setting': 'private',
            'account_role': 'gamer',
            'platforms[]': ['PlayStation', 'Xbox'],
            'gaming_usernames[]': ['john_doe_ps', 'john_doe_xbox'],
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(UserProfile.objects.filter(user=self.user).count(), 1)
        self.assertRedirects(response, reverse('userProfile:myProfile'))

    


