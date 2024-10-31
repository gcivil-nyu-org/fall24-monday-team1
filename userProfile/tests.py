# from django.test import TestCase, Client, RequestFactory
# from django.contrib.auth.models import User
# from django.urls import reverse
# from .models import UserProfile
# from django.core.files.uploadedfile import SimpleUploadedFile
# from .views import UserProfileListView

# # testcase for editProfile
# class EditProfileViewTest(TestCase):
#     def setUp(self):
#         # Create a test user and profile
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.profile = UserProfile.objects.create(user=self.user)
#         self.client = Client()
#         self.client.login(username='testuser', password='testpassword')
#         self.url = reverse('edit_profile')  # Update with actual URL pattern name if different

#     def test_get_request(self):
#         # Test the GET request for the editProfile view
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'editProfile.html')
#         self.assertIn('profile', response.context)

#     def test_post_update_profile_details(self):
#         # Test updating the profile's display name, bio, privacy, and account role
#         response = self.client.post(self.url, {
#             'display_name': 'New Display Name',
#             'bio': 'This is a new bio',
#             'privacy_setting': 'public',
#             'account_role': 'admin'
#         })
#         self.profile.refresh_from_db()
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(self.profile.display_name, 'New Display Name')
#         self.assertEqual(self.profile.bio, 'This is a new bio')
#         self.assertEqual(self.profile.privacy_setting, 'public')
#         self.assertEqual(self.profile.account_role, 'admin')

#     def test_post_upload_profile_photo(self):
#         # Test uploading a profile photo
#         profile_photo = SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg")
#         response = self.client.post(self.url, {
#             'profile_photo': profile_photo,
#         })
#         self.profile.refresh_from_db()
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(self.profile.profile_photo)

#     def test_post_update_gaming_usernames(self):
#         # Test updating gaming usernames with platform-based keys
#         response = self.client.post(self.url, {
#             'gaming_usernames[0]_platform': 'Steam',
#             'gaming_usernames[0]_username': 'gamer123',
#             'gaming_usernames[1]_platform': 'Xbox',
#             'gaming_usernames[1]_username': 'xboxPlayer'
#         })
#         self.profile.refresh_from_db()
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(self.profile.gaming_usernames['Steam'], 'gamer123')
#         self.assertEqual(self.profile.gaming_usernames['Xbox'], 'xboxPlayer')

#     def test_invalid_post_data(self):
#         # Test submitting invalid data (e.g., empty fields or invalid format)
#         response = self.client.post(self.url, {
#             'display_name': '',  # Empty display name
#             'privacy_setting': 'invalid_setting',  # Invalid privacy setting
#         })
#         self.assertEqual(response.status_code, 200)  # Should return the form with errors
#         self.assertFormError(response, 'form', 'display_name', 'This field is required.')
#         self.assertFormError(response, 'form', 'privacy_setting', 'Select a valid choice.')

#     def test_redirect_if_not_logged_in(self):
#         # Test that non-logged-in users are redirected to the login page
#         self.client.logout()
#         response = self.client.get(self.url)
#         self.assertRedirects(response, f'/accounts/login/?next={self.url}')


# #testcase for searchprofile

# class UserProfileListViewTests(TestCase):
#     def setUp(self):
#         # Create sample user profiles for testing
#         self.user1 = UserProfile.objects.create(display_name="Alice", privacy_setting="public", account_role="user")
#         self.user2 = UserProfile.objects.create(display_name="Bob", privacy_setting="private", account_role="admin")
#         self.user3 = UserProfile.objects.create(display_name="Charlie", privacy_setting="public", account_role="user")
#         self.factory = RequestFactory()

#     def test_no_filters_applied(self):
#         request = self.factory.get('/user-profiles/')
#         response = UserProfileListView.as_view()(request)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context_data['user_profiles']), 3)  # Should return all profiles

#     def test_filter_by_display_name(self):
#         request = self.factory.get('/user-profiles/', {'q': 'Alice'})
#         response = UserProfileListView.as_view()(request)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context_data['user_profiles']), 1)  # Should return only Alice's profile
#         self.assertEqual(response.context_data['user_profiles'][0].display_name, 'Alice')


# #testcase for viewprofile

# class UserProfileListViewTestCase(TestCase):
#     def setUp(self):
#         # Create a request factory
#         self.factory = RequestFactory()

#         # Create a user and some UserProfile instances with different settings
#         self.user = User.objects.create(username='testuser')
#         UserProfile.objects.create(user=self.user, display_name="John Doe", privacy_setting="public", account_role="admin")
#         UserProfile.objects.create(user=self.user, display_name="Jane Smith", privacy_setting="private", account_role="user")
#         UserProfile.objects.create(user=self.user, display_name="Alice", privacy_setting="public", account_role="guest")

#     def test_user_profile_list_view_filters(self):
#         # Create a GET request with query parameters for filtering
#         request = self.factory.get('/userprofiles/', {
#             'q': 'John',
#             'privacy': 'public',
#             'role': 'admin'
#         })

#         # Simulate a logged-in user
#         request.user = self.user

#         # Get the response from the UserProfileListView
#         response = UserProfileListView.as_view()(request)
#         context_data = response.context_data['user_profiles']

#         # Check if only the profile matching all filters is returned
#         self.assertEqual(len(context_data), 1)
#         self.assertEqual(context_data[0].display_name, "John Doe")
#         self.assertEqual(context_data[0].privacy_setting, "public")
#         self.assertEqual(context_data[0].account_role, "admin")