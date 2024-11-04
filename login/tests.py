from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupViewTests(TestCase):
    def setUp(self):
        # Create an existing user to test duplicate email and username
        self.existing_user = User.objects.create_user(username='existinguser', email='existing@example.com', password='testpass123')

    def test_signup_duplicate_email(self):
        response = self.client.post(reverse('signup'), {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 302)

    def test_signup_duplicate_username(self):
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'username': 'existinguser',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_signup_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'differentpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect due to error

    def test_signup_success(self):
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_pwd_validation(self):
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password1': '12345678',
            'password2': '12345678'
        })        
        self.assertEqual(response.status_code, 302)


class LoginViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testRootUser@gmail.com')

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_none_user(self):
        response = self.client.post(reverse('login'), {
            'username': '', 'password':'None'
        })
        self.assertEqual(response.status_code, 200)
    

