from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from management_app.models import Quiz
from management_app.utils.quiz_creator import create_quiz_from_url
from .serializers import QuizSerializer


class CreateQuizView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new Quiz from a provided video URL.
        """

        url = request.data.get('url')
        if not url:
            return Response({'detail': 'Ungültige URL oder Anfragedaten'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = create_quiz_from_url(url, request.user)
        except RuntimeError as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = QuizSerializer(quiz)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuizListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def get_queryset(self):
        """
        Returns quizzes belonging to the authenticated user.
        """
        return Quiz.objects.filter(user=self.request.user)
