import tempfile
import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from management_app.models import QuizQuestion, Quiz
from .serializers import QuizSerializer
import whisper
from google import genai
import json
import re
import yt_dlp


class CreateQuizView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a Quiz from a YouTube video URL by downloading the audio, transcribing it,
        generating quiz content using Gemini API, and saving it to the database.
        """

        url = request.data.get('url')
        if not url:
            return Response({'detail': 'Ungültige URL oder Anfragedaten'}, status=status.HTTP_400_BAD_REQUEST)

        if url.startswith('https://youtu.be/'):
            url = url.split("?")[0]
            url = url.replace('https://youtu.be/',
                              'https://www.youtube.com/watch?v=')

        with tempfile.NamedTemporaryFile(suffix='', delete=False) as tmp_file:
            tmp_audiofile = tmp_file.name

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": tmp_audiofile + ".%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            os.remove(tmp_audiofile)
            os.remove(tmp_audiofile + ".mp3")
            return Response({'detail': f'Error downloading audio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            model = whisper.load_model("turbo")
            result = model.transcribe(tmp_audiofile + ".mp3")
            transcript = result.get('text', '').strip()
        except Exception as e:
            os.remove(tmp_audiofile)
            os.remove(tmp_audiofile + ".mp3")
            return Response({'detail': f'Error transcribing audio: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        client = genai.Client(api_key=settings.MY_API_KEY)
        gemini_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="You will receive a transcript of a YouTube video. Using the content of this transcript, generate a quiz in the following structure:\n"
            "\n1. Create a title for the quiz.\n2. Create a description for the quiz.\n3. Generate one question directly based on the transcript.\n"
            "4. Generate four answer options, where exactly one is correct and the other three are incorrect but plausible.\n"
            "5. Save the correct answer separately in the field 'correct_answer'.\n"
            "\nYour answer must strictly follow this JSON structure:\n{\n  \"title\": \"generated title\",\n  \"description\": \"generated description\",\n  \"question\": \"generated question\",\n  \"answers\": [\"answer a\", \"answer b\", \"answer c\", \"answer d\"],\n  \"correct_answer\": \"The correct answer from 'answers'\"\n}\n\n"
            "Only use information from the transcript and do not add anything unrelated. Make the question clear and specific.\n\nTranscript:\n" + transcript
        )

        gemini_response = gemini_response.text
        cleaned_response = re.sub(r'^[^{]*', '', gemini_response)
        cleaned_response = cleaned_response.replace("`", "")
        cleaned_response = cleaned_response.strip()
        gemini_reponse_json = json.loads(cleaned_response)

        quiz = Quiz.objects.create(
            title=gemini_reponse_json["title"],
            description=gemini_reponse_json["description"],
            video_url=url,
            user=request.user
        )

        quiz_question = QuizQuestion.objects.create(
            quiz=quiz,
            question_title=gemini_reponse_json["question"],
            question_options=gemini_reponse_json["answers"],
            answer=gemini_reponse_json["correct_answer"]
        )

        os.remove(tmp_audiofile)
        os.remove(tmp_audiofile + ".mp3")

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
