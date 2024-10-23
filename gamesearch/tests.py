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
        mock_post.return_value.json.return_value = [
            {
                'id': 12345,
                'name': 'Test Game',
                'release_date': '2020',
                'cover': {
                    'url': '//images.igdb.com/cover_url.jpg'
                },
                'genres': [{'name': 'Action'}, {'name': 'Adventure'}]
            }
        ]

        search_query = 'Test Game'
        response = self.client.post(reverse('gamesearch:search_game'), {
            'game_query': search_query
        })
        print(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn('games', response.context)  # Search results returned
        self.assertContains(response, 'Test Game')  # Game title is displayed

        ### Step 3: Click on a Game and View Game Details
        # Mock the game details API response
        mock_post.return_value.json.return_value = [{
            'name': 'Test Game',
            'genres': [{'name': 'Action'}, {'name': 'Adventure'}],
            'first_release_date': 1609459200,
            'summary': 'Test Game summary.',
            'cover': 'images.igdb.com/cover_url.jpg'
        }]
        
        response = self.client.get(reverse('gamesearch:game-details', args=[12345]))
        self.assertEqual(response.status_code, 200)  # Game details fetched

        ### Step 4: Test Adding Game to Shelf
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