from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        token = response.cookies.get('access_token').value
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_logout_success(self):
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)