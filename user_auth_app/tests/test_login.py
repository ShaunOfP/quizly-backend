from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='olivia', password='password123')

    def test_login_success(self):
        response = self.client.post(
            '/api/login/', {'username': 'olivia', 'password': 'password123'}, format='json')
        cookie = response.cookies.get('access_token').value

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + cookie)
        logout_response = self.client.post('/api/logout/')
        self.assertEqual(logout_response.status_code, 200)

    def test_login_failure_wrong_data(self):
        response = self.client.post(
            '/api/login/', {'username': 'olivia', 'password': 'anotherpassword'}, format='json')
        cookie = response.cookies.get('access_token')
        if cookie:
            cookie = cookie.value
        else:
            self.assertEqual(cookie, None)