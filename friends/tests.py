from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import FriendRequest

class FriendRequestTests(TestCase):
    def setUp(self):
        # Get the custom user model
        User = get_user_model()
        
        # Create test users
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass1',
            email='test1@example.com'  # Required for CheckpointUser
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass2',
            email='test2@example.com'
        )
        self.user3 = User.objects.create_user(
            username='testuser3',
            password='testpass3',
            email='test3@example.com'
        )
        
        # Log in user1
        self.client.login(username='testuser1', password='testpass1')

    def test_send_friend_request(self):
        # Send friend request from user1 to user2
        response = self.client.post(reverse('friends:send_request', args=['testuser2']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Verify request exists
        requests = FriendRequest.get_pending_requests('testuser2')
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['from_user'], 'testuser1')

    def test_accept_friend_request(self):
        # Create a friend request
        FriendRequest.send_request('testuser2', 'testuser1')
        
        # Accept the request
        response = self.client.post(reverse('friends:accept_request', args=['testuser2']))
        self.assertEqual(response.status_code, 302)  # Redirects after acceptance

        # Verify friendship is established
        friends = FriendRequest.get_friends('testuser1')
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]['username'], 'testuser2')

    def test_reject_friend_request(self):
        # Create a friend request from user2 to user1
        FriendRequest.send_request('testuser2', 'testuser1')
        
        # Login as user1 who will reject the request
        self.client.login(username='testuser1', password='testpass1')
        
        # User1 rejects the request from user2
        response = self.client.post(reverse('friends:reject_request', args=['testuser2']))
        self.assertEqual(response.status_code, 302)  # Redirects after rejection

        # Verify request is removed
        requests = FriendRequest.get_pending_requests('testuser1')
        self.assertEqual(len(requests), 0)

    def test_unfriend(self):
        # Create friendship
        FriendRequest.send_request('testuser2', 'testuser1')
        FriendRequest.accept_request('testuser2', 'testuser1')
        
        # Unfriend
        response = self.client.post(reverse('friends:unfriend', args=['testuser2']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        # Verify friendship is removed
        friends = FriendRequest.get_friends('testuser1')
        self.assertEqual(len(friends), 0)

    def test_view_friend_list(self):
        # Create some friendships
        FriendRequest.send_request('testuser2', 'testuser1')
        FriendRequest.accept_request('testuser2', 'testuser1')
        
        response = self.client.get(reverse('friends:friend_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('friends' in response.context)
        self.assertEqual(len(response.context['friends']), 1)

    def test_view_friend_requests(self):
        # Create pending requests
        FriendRequest.send_request('testuser2', 'testuser1')
        FriendRequest.send_request('testuser3', 'testuser1')
        
        response = self.client.get(reverse('friends:friend_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('received_requests' in response.context)
        self.assertEqual(len(response.context['received_requests']), 2)
