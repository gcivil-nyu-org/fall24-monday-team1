# gamesearch/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from login.models import CheckpointUser
import json

class GameSearchWorkflowTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = CheckpointUser.objects.create_user(username='testuser', password='password')

        self.client.login(username='testuser', password='password')

    def test_game_search_workflow(self):

        # Check if we are getting the page first
        response = self.client.get(reverse('gamesearch:search_game'))
        self.assertEqual(response.status_code, 200)  # Profile page accessible
        self.assertTemplateUsed(response, 'search.html')  # Search template rendered


        # Mock the IGDB Return value and make a mock API call
        with patch('gamesearch.views.requests.post') as mock_post:
            mock_post.return_value.json.return_value = [{
                'id': 26192, 
                'name': 'The Last of Us Part II', 
                'img_url': 'images.igdb.com/igdb/image/upload/t_thumb/co5ziw.jpg', 
                'release_date': '2020-06-19'}
            ]
            mock_post.status_code = 200

            search_query = 'the last of us'
            response = self.client.post(reverse('gamesearch:search_game'), {
                'game_query': search_query
            })

            self.assertEqual(response.status_code, 200)

            mock_post.return_value.json.return_value = {
                'id': 1009, 
                'cover': 
                'images.igdb.com/igdb/image/upload/t_thumb/co1r7f.jpg', 
                'release_year': 
                '2013', 
                'genres': ['Shooter', 'Adventure'], 
                'name': 'The Last of Us', 
                'platforms': ['PlayStation 3'], 
                'rating': 92.97792061273745, 
                'summary': 'Sample Summary', 
                'url': 'https://www.igdb.com/games/the-last-of-us'
            }
            
            response = self.client.get(reverse('gamesearch:game-details', args=[1009]))
            self.assertEqual(response.status_code, 200)  # Game details fetched


        # Mocking the DynamoDB operation for adding a game to the shelf
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.get_item.return_value = {}
            mock_table.put_item.return_value = {'status': 'success'}

            response = self.client.post(reverse('gamesearch:save_to_shelf'), {
                'game_id': 12345,
                'shelf_name': 'completed'
            })

            
            self.assertEqual(response.status_code, 200)  # POST request successful
            self.assertJSONEqual(response.content, {'status': 'success'})  # Game added to shelf


            mock_table.get_item.return_value = {
                'Item': {
                    'user_id': self.user.username,
                    'completed': ["12345"]  # Game ID already exists in "completed" shelf
                }
            }
            mock_table.put_item.return_value = {'status': 'alreadyExists'}

            response = self.client.post(reverse('gamesearch:save_to_shelf'), {
                'game_id': "12345",
                'shelf_name': 'completed'
            })


            
            self.assertEqual(response.status_code, 200)  # POST request successful
            self.assertJSONEqual(response.content, {'status': 'alreadyExists'})  # Game added to shelf


            mock_table.get_item.return_value = {
                'Item': {
                    'user_id': self.user.username,
                    'want-to-play': ["12345"],  # Game ID already exists in another shelf ("want to play")
                    'completed': [],
                    "abandoned": [],
                    "playing": [],
                    "paused": []
                }
            }
            mock_table.put_item.return_value = {'status': 'movedShelf'}

            response = self.client.post(reverse('gamesearch:save_to_shelf'), {
                'game_id': "12345",
                'shelf_name': 'completed'
            })


            
            # self.assertEqual(response.status_code, 200)  # POST request successful
            # self.assertJSONEqual(response.content, {'status': 'movedShelf'})  # Game added to shelf

        