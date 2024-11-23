from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from userProfile.models import UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from .views import user_profile_list
import json
from django.contrib.auth import get_user_model
from unittest.mock import patch


User = get_user_model()

# testcase for editProfile
class EditProfileViewTest(TestCase):
    def setUp(self):
        # Create a test user and profile
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = UserProfile.objects.create(user=self.user)
        self.profile.display_name = "john"
        self.profile.save()
        self.client.login(username='testuser', password='testpassword')
        self.url = reverse('userProfile:editProfile')  # Update with actual URL pattern name if different

    def test_get_request(self):
        # Test the GET request for the editProfile view
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editProfile.html')
        self.assertIn('profile', response.context)

    def test_post_update_profile_details(self):
        # Test updating the profile's display name, bio, privacy, and account role
        response = self.client.post(self.url, {
            'display_name': 'New Display Name',
            'bio': 'This is a new bio',
            'privacy_setting': 'public',
            'account_role': 'gamer'
        })
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.profile.display_name, 'New Display Name')
        self.assertEqual(self.profile.bio, 'This is a new bio')
        self.assertEqual(self.profile.privacy_setting, 'public')
        self.assertEqual(self.profile.account_role, 'gamer')


    def test_post_update_gaming_usernames(self):
        # Test updating gaming usernames with platform-based keys
        post_data = {
            'display_name': 'John',
            'bio': 'orihg',
            'privacy_setting': 'private',
            'account_role': 'gamer',
            'gaming_usernames[xbox]': ['xboxPlayer'],
            'gaming_usernames[steam]': ['gamer123'],
        }
        
        response = self.client.post(reverse('userProfile:editProfile'), data=post_data)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(profile.gaming_usernames['steam'], 'gamer123')
        self.assertEqual(profile.gaming_usernames['xbox'], 'xboxPlayer')



# #testcase for searchprofile

class UserProfileListViewTests(TestCase):
    def setUp(self):
        # Create sample user profiles for testing
        self.factory = RequestFactory()

        # Create a user and some UserProfile instances with different settings
        self.user1 = User.objects.create(username='testuser1', password='testpass', email='user1@dom.com')
        self.user2 = User.objects.create(username='testuser2', password='testpass', email='user2@dom.com')
        self.user3 = User.objects.create(username='testuser3', password='testpass', email='user3@dom.com')
        UserProfile.objects.create(user=self.user1, display_name="John Doe", privacy_setting="public", account_role="gamer")
        UserProfile.objects.create(user=self.user2, display_name="Jane Smith", privacy_setting="private", account_role="creator")
        UserProfile.objects.create(user=self.user3, display_name="Alice", privacy_setting="public", account_role="event_organizer")

    def test_no_filters_applied(self):
        self.client.login(username='user1', password='password')  # Log in user1
        response = self.client.get(reverse('userProfile:searchProfile'))  # Use reverse to get the URL
        
        self.assertEqual(response.status_code, 200)
        user_profiles = response.context['user_profiles']  # Access context
        self.assertEqual(len(user_profiles), 2)  # Should return all profiles excluding user1's profile

    def test_filter_by_display_name(self):
        self.client.login(username='user1', password='password')  # Log in user1
        response = self.client.get(reverse('userProfile:searchProfile'), {'q': 'Alice'})  # Use reverse to get the URL with query param
        
        self.assertEqual(response.status_code, 200)
        user_profiles = response.context['user_profiles']  # Access context
        self.assertEqual(len(user_profiles), 1)  # Should return only Alice's profile
        self.assertEqual(user_profiles[0].display_name, 'Alice')


class UserProfileViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass", email="test1@dom.com")
        self.other_user = User.objects.create_user(username="otheruser", password="otherpass", email="test2@dom.com")
        self.client.login(username="testuser", password="testpass")

        self.profile = UserProfile.objects.create(
            user=self.user,
            display_name="Test User",
            privacy_setting="public",
            gaming_usernames=json.dumps({"Xbox": "test_xbox", "PSN": "test_psn"})
        )

        self.profile2 = UserProfile.objects.create(
            user=self.other_user,
            display_name="Test User 2",
            privacy_setting="public",
            gaming_usernames=json.dumps({"Xbox": "test_xbox", "PSN": "test_psn"})
        )

    def test_view_profile_public(self):
        # Mock DynamoDB response for user game shelves
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.get_item.return_value = {
                'Item': {
                    'user_id': self.user.username,
                    'completed': ['1009', '26192'],
                    'playing': [],
                    'abandoned': [],
                    'paused': [],
                    'want-to-play': []
                }
            }

            response = self.client.get(reverse('userProfile:viewProfile', args=[self.other_user.id]))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['viewable'])
            self.assertEqual(response.context['user_games'], {
                'completed': ['1009', '26192'],
                'playing': [],
                'abandoned': [],
                'paused': [],
                'want-to-play': []
            })
            self.assertEqual(response.context['gaming_usernames'], {"Xbox": "test_xbox", "PSN": "test_psn"})

    def test_view_profile_private_for_another_user(self):
        # Change privacy setting to "friends_only"
        self.profile.privacy_setting = "friends_only"
        self.profile.save()

        # Other user views the profile (should not be viewable)
        self.client.logout()
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(reverse('userProfile:viewProfile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['viewable'])