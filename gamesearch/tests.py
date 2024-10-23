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

    @patch('gamesearch.views.requests.post')  # Mocking IGDB API requests
    def test_game_search_workflow(self, mock_post):

        # Check if we are getting the page first
        response = self.client.get(reverse('gamesearch:search_game'))
        self.assertEqual(response.status_code, 200)  # Profile page accessible
        self.assertTemplateUsed(response, 'search.html')  # Search template rendered


        # Mock the IGDB Return value and make a mock API call
        # TODO: make it not actually call IGDB
        
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

        # User clicks on game, mock the response
        mock_post.return_value.json.return_value = {'id': 1009, 'cover': 'images.igdb.com/igdb/image/upload/t_thumb/co1r7f.jpg', 'release_year': '2013', 'genres': ['Shooter', 'Adventure'], 'name': 'The Last of Us', 'platforms': ['PlayStation 3'], 'rating': 92.97792061273745, 'summary': 'A third person shooter/stealth/survival hybrid, in which twenty years after the outbreak of a parasitic fungus which takes over the neural functions of humans, Joel, a Texan with a tragic familial past, finds himself responsible with smuggling a fourteen year old girl named Ellie to a militia group called the Fireflies, while avoiding strict and deadly authorities, infected fungal hosts and other violent survivors.', 'url': 'https://www.igdb.com/games/the-last-of-us'}
        
        response = self.client.get(reverse('gamesearch:game-details', args=[1009]))
        self.assertEqual(response.status_code, 200)  # Game details fetched


        # Mocking the DynamoDB operation for adding a game to the shelf
        with patch('gamesearch.views.boto3.resource') as mock_dynamo:
            mock_table = mock_dynamo.return_value.Table.return_value
            mock_table.get_item.return_value = {}
            mock_table.put_item.return_value = {}

            response = self.client.post(reverse('gamesearch:save_to_shelf'), {
                'game_id': 12345,
                'shelf_name': 'completed'
            })
            
            self.assertEqual(response.status_code, 200)  # POST request successful
            self.assertJSONEqual(response.content, {'status': 'success'})  # Game added to shelf

        mock_table.get_item.return_value = {'Item': {
            'user_id': 'testuser',
            'completed': [12345],
            'playing': [],
            'want-to-play': [],
            'abandoned': [],
            'paused': []
        }}

        response = self.client.post(reverse('gamesearch:save_to_shelf'), {
            'game_id': 12345,
            'shelf_name': 'completed'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'alreadyExists'})