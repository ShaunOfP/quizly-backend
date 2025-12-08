from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse


class RefreshTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        response = self.client.post(
            '/api/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        refresh_token = response.cookies.get('refresh_token').value
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + refresh_token)
        self.client.cookies['refresh_token'] = refresh_token

    def test_token_refresh_success(self):
        refresh_response = self.client.post('/api/token/refresh/')
        self.assertEqual(refresh_response.status_code, 200)

    def test_token_refresh_no_cookie(self):
        self.client.cookies.pop('refresh_token', None)
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 403)

    def test_token_refresh_invalid_cookie(self):
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 401)
