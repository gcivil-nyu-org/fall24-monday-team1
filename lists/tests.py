from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import boto3
from botocore.stub import Stubber
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()

class ListViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_list_view_requires_login(self):
        """Test that the create_list view requires a login"""
        self.client.logout()
        response = self.client.get(reverse('lists:create_list'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect to login page

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('lists:create_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_list.html')


    
    def test_save_list_success(self):
        # Set up DynamoDB table mock
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_dynamo.return_value.Table.return_value = mock_table

            list_data = {
                'name': 'Test List',
                'description': 'This is a test list description.',
                'visibility': 'public',
                'games[]': json.dumps([
                    {"id": "72373", "name": "game1"},
                    {"id": "265111", "name": "game2"}
                ])
            }
            
            response = self.client.post(reverse('lists:save_list'), data=list_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json().get('status'), 'success')
            

    def test_save_list_dynamo_error(self):
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = None
            mock_dynamo.return_value.Table.return_value = mock_table

            list_data = {
                'name': 'Error List',
                'description': 'This list will trigger a DynamoDB error.',
                'visibility': 'private',
                'games[]': json.dumps([{"id": "1111", "name": "Error Game"}])
            }
            response = self.client.post(reverse('lists:save_list'), data=list_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json().get('status'), 'failedToPutToDynamo')
    
    def test_data_error(self):
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_dynamo.return_value.Table.return_value = mock_table

            list_data = {}
            response = self.client.post(reverse('lists:save_list'), data=list_data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json().get('status'), 'error')