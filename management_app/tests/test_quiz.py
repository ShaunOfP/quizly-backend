from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User

from management_app.models import Quiz, QuizQuestion


class QuizTests(APITestCase):
    def setUp(self):
        """
        Registrates the testuser for the testcase and generates a test quiz.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        response = self.client.post(
            '/api/login/', {'username': 'testuser', 'password': 'testpass'}, format='json')
        access_token = response.cookies.get('access_token').value
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + access_token)
        self.quiz = Quiz.objects.create(
            title='Sample Quiz', user=self.user, description='A sample quiz for testing.',
            video_url='http://example.com/video')
        self.quiz_question = QuizQuestion.objects.create(
            question_title='Sample Question',
            question_options=['Option 1', 'Option 2', 'Option 3', 'Option 4'],
            answer='Option 1',
            quiz=self.quiz
        )

    def test_create_quiz(self):
        url = reverse('create_quiz')
        data = {
            'url': 'https://www.youtube.com/watch?v=PPzIWFJU_3s'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_quizzes(self):
        url = reverse('quiz_list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_quiz_detail(self):
        detail_url = reverse('quiz_detail', kwargs={'pk': self.quiz.id})
        detail_response = self.client.get(detail_url, format='json')
        self.assertEqual(detail_response.status_code, 200)

    def test_update_quiz(self):
        detail_url = reverse('quiz_detail', kwargs={'pk': self.quiz.id})
        update_data = {
            'title': 'Updated Sample Quiz',
            'description': 'An updated sample quiz for testing.'
        }
        update_response = self.client.put(
            detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['title'], 'Updated Sample Quiz')
        self.assertEqual(
            update_response.data['description'], 'An updated sample quiz for testing.')

    def test_delete_quiz(self):
        detail_url = reverse('quiz_detail', kwargs={'pk': self.quiz.id})
        delete_response = self.client.delete(detail_url, format='json')
        self.assertEqual(delete_response.status_code, 204)
        get_response = self.client.get(detail_url, format='json')
        self.assertEqual(get_response.status_code, 404)
