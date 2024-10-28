from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

class CommentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testRootUser@gmail.com')
        self.client.login(username='testuser', password='testpass')
        self.root_comment = Comment.objects.create(author=self.user, content='Root comment', is_root=True)

    def test_create_reply(self):
        response = self.client.post(reverse('create_reply', args=[self.root_comment.id]), {
            'content': 'This is a reply',
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(self.root_comment.replies.count(), 1)
        self.assertEqual(self.root_comment.replies.first().content, 'This is a reply')

    def test_edit_comment(self):
        response = self.client.post(reverse('edit_comment', args=[self.root_comment.id]), {
            'content': 'Edited content',
            'curPath': '/comments/test/'
        })
        self.root_comment.refresh_from_db()
        self.assertEqual(self.root_comment.content, 'Edited content')
        self.assertEqual(response.status_code, 302)  # Check for redirect

    def test_edit_comment_not_author(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass', email='otherUserTest@gmail.com')
        self.client.logout()
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('edit_comment', args=[self.root_comment.id]), {
            'content': 'Hacker edit',
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 403)  # Check for forbidden access
        other_user.delete()

    def test_delete_comment(self):
        response = self.client.post(reverse('delete_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(Comment.objects.count(), 0)  # Comment should be deleted

    def test_delete_comment_not_author(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass', email='otherUserTest@gmail.com')
        self.client.logout()
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(reverse('delete_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 403)  # Check for forbidden access
        other_user.delete()

    def test_upvote_comment(self):
        response = self.client.post(reverse('upvote_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertIn(self.user, self.root_comment.upvote.all())

    def test_downvote_comment(self):
        response = self.client.post(reverse('downvote_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertIn(self.user, self.root_comment.downvote.all())

    def test_upvote_and_remove(self):
        self.root_comment.upvote.add(self.user)
        response = self.client.post(reverse('upvote_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertNotIn(self.user, self.root_comment.upvote.all())

    def test_downvote_and_remove(self):
        self.root_comment.downvote.add(self.user)
        response = self.client.post(reverse('downvote_comment', args=[self.root_comment.id]), {
            'curPath': '/comments/test/'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertNotIn(self.user, self.root_comment.downvote.all())

    def test_get_or_create_comment_board(self):
        # Test comment board creation
        board_comment = Comment.objects.create(content='Test Board', is_root=True)
        self.assertIsNotNone(board_comment)
        self.assertEqual(board_comment.content, 'Test Board')
        self.assertTrue(board_comment.is_root)

    def tearDown(self):
        self.user.delete()
        self.root_comment.delete()