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
        
        # Clean up any existing test data
        self.clean_test_data()
        
        # Log in user1
        self.client.login(username='testuser1', password='testpass1')

    def clean_test_data(self):
        """Clean up only test-related data"""
        test_users = ['testuser1', 'testuser2', 'testuser3']
        
        # Clean friend requests table
        requests_table = FriendRequest.get_friend_requests_table()
        if requests_table:
            # Clean requests where either to_user or from_user is a test user
            for test_user in test_users:
                # Check requests received by test user
                response = requests_table.query(
                    KeyConditionExpression='to_user = :user',
                    ExpressionAttributeValues={':user': test_user}
                )
                for item in response.get('Items', []):
                    requests_table.delete_item(
                        Key={
                            'to_user': item['to_user'],
                            'from_user': item['from_user']
                        }
                    )
                
                # Check requests sent by test user using GSI
                response = requests_table.query(
                    IndexName='from_user-index',
                    KeyConditionExpression='from_user = :user',
                    ExpressionAttributeValues={':user': test_user}
                )
                for item in response.get('Items', []):
                    requests_table.delete_item(
                        Key={
                            'to_user': item['to_user'],
                            'from_user': item['from_user']
                        }
                    )
        
        # Clean friends table
        friends_table = FriendRequest.get_friends_table()
        if friends_table:
            # Clean friendships where either user is a test user
            for test_user in test_users:
                response = friends_table.query(
                    KeyConditionExpression='username = :user',
                    ExpressionAttributeValues={':user': test_user}
                )
                for item in response.get('Items', []):
                    friends_table.delete_item(
                        Key={
                            'username': item['username'],
                            'friend': item['friend']
                        }
                    )

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
        
        # Verify request exists before rejection
        requests_before = FriendRequest.get_pending_requests('testuser1')
        self.assertEqual(len(requests_before), 1)
        
        # User1 rejects the request from user2
        response = self.client.post(reverse('friends:reject_request', args=['testuser2']))
        self.assertEqual(response.status_code, 302)  # Redirects after rejection

        # Verify request is removed
        requests_after = FriendRequest.get_pending_requests('testuser1')
        self.assertEqual(len(requests_after), 0)

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
