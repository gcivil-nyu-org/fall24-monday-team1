# gamesearch/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from login.models import CheckpointUser

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

    def test_game_details_workflow(self):
        with patch('gamesearch.views.requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'id': 19560,
             'cover': 'images.igdb.com/igdb/image/upload/t_thumb/co1tmu.jpg',
             'release_year': '2018',
             'genres': ['Role-playing (RPG)', "Hack and slash/Beat 'em up", 'Adventure'],
             'name': 'God of War',
             'platforms': ['PC (Microsoft Windows)', 'PlayStation 4'],
             'rating': 92.8721133076585,
             'summary': 'God of War is the sequel to God of War III as well as a\
                continuation of the canon God of War chronology. Unlike previous\
                installments, this game focuses on Norse mythology and follows\
                an older and more seasoned Kratos and his son Atreus in the\
                years since the third game. It is in this harsh, unforgiving\
                world that he must fight to survive… and teach his son to do the same.',
             'url': 'https://www.igdb.com/games/god-of-war--1'}
            response = self.client.get(reverse('gamesearch:game-data-fetch', args=[19560]))
            self.assertEqual(response.status_code, 200)
    

    def test_missing_name_in_search_result(self):
        with patch('gamesearch.views.requests.post') as mock_post:
            mock_post.return_value.json.return_value = [{
                'id': 26192, 
                'img_url': 'images.igdb.com/igdb/image/upload/t_thumb/co5ziw.jpg', 
                'release_date': '2020-06-19'}
            ]
            mock_post.status_code = 200

            search_query = 'the last of us'
            response = self.client.post(reverse('gamesearch:search_game'), {
                'game_query': search_query
            })
            self.assertEqual(response.status_code, 200)
        