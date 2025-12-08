from rest_framework.test import APITestCase
from django.urls import reverse


class RegistrationTests(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'confirmed_password': 'newpassword123',
            'email': 'new@user.de'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_registration_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'confirmed_password': 'differentpassword',
            'email': 'new@user.de'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_missing_fields(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            # 'password' is missing
            'confirmed_password': 'newpassword123',
            'email': 'new@user.de'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)