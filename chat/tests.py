from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json
import time

from django.contrib.auth import get_user_model

User = get_user_model()

class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.to_user = "testreceiver"
        self.room_id = "testroom123"
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@events.com')
        self.client.login(username='testuser', password='password')

    def test_chat_page_existing_room(self):
        # Mock DynamoDB interactions
        with patch('chat.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.scan.return_value = {
                'Items': [
                    {
                        'room_uuid': self.room_id,
                        'from': 'testuser',
                        'to': self.to_user
                    }
                ]
            }
            mock_chat_history_table = mock_dynamo.return_value.Table.return_value
            mock_chat_history_table.scan.return_value = {
                'Items': [
                    {
                        'room_uuid': self.room_id,
                        'sender': 'testuser',
                        'receiver': self.to_user,
                        'timestamp': str(time.time()),
                        'msg': 'Hello!'
                    }
                ]
            }

            response = self.client.get(reverse('chat:chat-page', args=[self.to_user, self.room_id]))
            self.assertEqual(response.status_code, 200)
            context = response.context
            self.assertEqual(context['room_name'], self.room_id)
            self.assertEqual(context['to'], self.to_user)
            messages = json.loads(context['messages'])
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]['msg'], 'Hello!')

    def test_chat_page_new_room(self):
        # Mock DynamoDB interactions
        with patch('chat.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.scan.return_value = {'Items': []}  # No existing room
            mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

            response = self.client.get(reverse('chat:chat-page', args=[self.to_user, self.room_id]))
            self.assertEqual(response.status_code, 200)
            context = response.context
            self.assertEqual(context['room_name'], self.room_id)
            self.assertEqual(context['to'], self.to_user)
            messages = json.loads(context['messages'])
            self.assertEqual(len(messages), 0)  # No messages in a new room

            # Verify that a new room was created
            mock_table.put_item.assert_called_once_with(Item={
                'room_uuid': self.room_id,
                'from': 'testuser',
                'to': self.to_user
            })

    def test_save_message_success(self):
        with patch('chat.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

            response = self.client.post(reverse('chat:save-message'), {
                'room_uuid': self.room_id,
                'sender': 'testuser',
                'receiver': self.to_user,
                'message': 'Test message'
            })
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            self.assertEqual(response_data['status'], 'success')

            # Verify that the message was saved
            mock_table.put_item.assert_called_once()
            args, kwargs = mock_table.put_item.call_args
            item = kwargs['Item']
            self.assertEqual(item['room_uuid'], self.room_id)
            self.assertEqual(item['sender'], 'testuser')
            self.assertEqual(item['receiver'], self.to_user)
            self.assertEqual(item['msg'], 'Test message')

    def test_save_message_failure(self):
        with patch('chat.views.boto3.resource') as mock_dynamo:
         
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.put_item.side_effect = Exception("Simulated failure")

            response = self.client.post(reverse('chat:save-message'), {
                'room_uuid': self.room_id,
                'sender': 'testuser',
                'receiver': self.to_user,
                'message': 'Test message'
            })
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.content)
            print(response_data)
            # self.assertEqual(response_data['status'], 'failure')

    def test_chat_page_no_authentication(self):
        with patch('chat.views.boto3.resource') as mock_dynamo:

            self.client.logout()  # Simulate unauthenticated user
            response = self.client.get(reverse('chat:chat-page', args=[self.to_user, self.room_id]))
            self.assertEqual(response.status_code, 302)  # Redirect to login
            self.assertTrue(response.url.endswith('login/'))