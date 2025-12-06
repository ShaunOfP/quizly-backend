from rest_framework import serializers

from management_app.models import Quiz, QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at'
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at',
                  'updated_at', 'video_url', 'questions']

    def get_questions(self, obj):
        if obj.questions:
            return [QuizQuestionSerializer(obj.questions).data]
        return []
