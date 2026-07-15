"""Tests for the accounts app: models, registration and JWT auth."""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from accounts.models import User, Profile


class RegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_creates_user(self):
        url = reverse('api-register')
        data = {
            'username': 'alice', 'email': 'alice@example.com',
            'password': 'supersecret1', 'password2': 'supersecret1',
            'first_name': 'Alice',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='alice')
        self.assertTrue(user.check_password('supersecret1'))
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username='bob', email='dup@example.com', password='x1')
        url = reverse('api-register')
        data = {
            'username': 'bob2', 'email': 'dup@example.com',
            'password': 'supersecret1', 'password2': 'supersecret1',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)


class JWTAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='carol', email='carol@example.com', password='supersecret1'
        )

    def test_login_returns_tokens(self):
        url = reverse('api-login')
        response = self.client.post(
            url, {'username': 'carol@example.com', 'password': 'supersecret1'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_me_requires_auth(self):
        url = reverse('api-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        # With token it succeeds.
        login = self.client.post(
            reverse('api-login'),
            {'username': 'carol@example.com', 'password': 'supersecret1'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'carol@example.com')
