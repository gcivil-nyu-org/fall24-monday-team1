from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
import json
import boto3
from botocore.stub import Stubber
import uuid
from django.contrib.auth import get_user_model
from lists.views import get_lists
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


from django.test import TestCase, RequestFactory

class GetListsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up the test user
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.factory = RequestFactory()

    def test_create_list_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('lists:view_lists'))
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('lists:view_lists'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_lists.html')

    def test_get_lists_my_tab(self):
        # Mock DynamoDB resource and table
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_dynamo.return_value.Table.return_value = mock_table


            # Mock the response from DynamoDB
            mock_table.scan.return_value = {
                'Items': [
                    {
                        'name': 'My List 1',
                        'description': 'A description',
                        'username': 'testuser',
                        'games': [{'id': 1}, {'id': 2}]
                    },
                    {
                        'name': 'My List 2',
                        'description': 'Another description',
                        'username': 'testuser',
                        'games': [{'id': 3}]
                    }
                ],
                'LastEvaluatedKey': None  # No more pages
            }

            request = self.factory.get('/lists/?tab=my', HTTP_USER_AGENT='test')
            request.user = self.user  # Set the user to the current test user

            # Call the view
            response = get_lists(request)

            # Assert the status code and returned data
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(len(data['lists']), 2)
            self.assertEqual(data['lists'][0]['creator'], 'testuser')

    def test_get_lists_discover_tab(self):
        # Mock DynamoDB resource and table
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_dynamo.return_value.Table.return_value = mock_table


            # Mock the response from DynamoDB
            mock_table.scan.return_value = {
                'Items': [
                    {
                        'name': 'My List 1',
                        'description': 'A description',
                        'username': 'testuser',
                        'games': [{'id': 1}, {'id': 2}]
                    },
                    {
                        'name': 'My List 2',
                        'description': 'Another description',
                        'username': 'testuser',
                        'games': [{'id': 3}]
                    }
                ],
                'LastEvaluatedKey': None  # No more pages
            }

            request = self.factory.get('/lists/?tab=discover', HTTP_USER_AGENT='test')
            request.user = self.user  # Set the user to the current test user

            # Call the view
            response = get_lists(request)

            # Assert the status code and returned data
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(len(data['lists']), 2)
            self.assertEqual(data['lists'][0]['creator'], 'testuser')