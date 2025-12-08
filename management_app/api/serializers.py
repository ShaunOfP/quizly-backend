from rest_framework import serializers

from management_app.models import Quiz, QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at'
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at',
                  'updated_at', 'video_url', 'questions']
        read_only_fields = ['id', 'created_at',
                            'updated_at', 'questions', 'video_url']

    def get_questions(self, obj):
        """
        If the Quiz has a related QuizQuestion, it serializes that question
        and wraps it in a list. If no question is associated, returns an empty list.
        """
        if obj.questions:
            return [QuizQuestionSerializer(obj.questions).data]
        return []
