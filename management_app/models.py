from django.db import models
from django.contrib.auth.models import User


class QuizQuestion(models.Model):
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='questions')


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
