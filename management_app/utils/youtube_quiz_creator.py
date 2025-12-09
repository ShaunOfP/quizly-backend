import tempfile
import os
from django.conf import settings

from management_app.models import QuizQuestion, Quiz
import whisper
from google import genai
import json
import re
import yt_dlp


def create_quiz_from_url(url: str, user):
    """
    Given a YouTube video URL, this function downloads the audio, transcribes it,
    generates quiz content using Gemini API, and saves it to the database.
    """
    if url.startswith('https://youtu.be/'):
        url = url.split("?")[0]
        url = url.replace('https://youtu.be/',
                          'https://www.youtube.com/watch?v=')

    with tempfile.NamedTemporaryFile(suffix='', delete=False) as tmp_file:
        tmp_audiofile = tmp_file.name

    download_audio_from_video(url, tmp_audiofile)

    transcript = generate_transcript(tmp_audiofile)

    gemini_response = get_ai_response(transcript)

    gemini_response_json = clean_ai_response(gemini_response.text)

    quiz = Quiz.objects.create(
        title=gemini_response_json["title"],
        description=gemini_response_json["description"],
        video_url=url,
        user=user
    )

    for item in gemini_response_json['questions']:
        QuizQuestion.objects.create(
            quiz=quiz,
            question_title=item["question_title"],
            question_options=item["question_options"],
            answer=item["answer"]
        )

    cleanup_temp_files(tmp_audiofile)

    return quiz


def cleanup_temp_files(*file_paths):
    """
    Removes temporary files created during the quiz creation process.
    """
    for file_path in file_paths:
        try:
            os.remove(file_path)
            os.remove(file_path + ".mp3")
        except OSError:
            pass


# region Prepare Quiz Generation
def download_audio_from_video(url: str, tmp_audiofile: str):
    """
    Downloads audio from a YouTube video URL and saves it as an MP3 file.
    """
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
        cleanup_temp_files(tmp_audiofile)
        raise RuntimeError(f'Error downloading audio: {str(e)}')


def generate_transcript(tmp_audiofile: str):
    """
    Transcribes audio from an MP3 file using the Whisper model and returns the transcript.
    """
    try:
        model = whisper.load_model("turbo")
        result = model.transcribe(tmp_audiofile + ".mp3")
        transcript = result.get('text', '').strip()
        return transcript
    except Exception as e:
        cleanup_temp_files(tmp_audiofile)
        raise RuntimeError(f'Error transcribing audio: {str(e)}')
# endregion

# region Quiz generation and Response Formatting


def get_ai_response(transcript: str):
    """
    Generates quiz content using the Gemini API based on the provided transcript.
    """
    client = genai.Client(api_key=settings.MY_API_KEY)
    gemini_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Based on the following transcript, generate a quiz in valid JSON format.\n\n"
        "The quiz must follow this exact structure:\n\n"
        "{\n"
        "  \"title\": \"Create a concise quiz title based on the topic of the transcript.\",\n"
        "  \"description\": \"Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.\",\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question_title\": \"The question goes here.\",\n"
        "      \"question_options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "      \"answer\": \"The correct answer from the above options\"\n"
        "    },\n"
        "    ... (exactly 10 questions)\n"
        "  ]\n"
        "}\n\n"
        "Requirements:\n"
        "- Each question must have exactly 4 distinct answer options.\n"
        "- Only one correct answer is allowed per question, and it must be present in 'question_options'.\n"
        "- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).\n"
        "- Do not include explanations, comments, or any text outside the JSON.\n"
        "Transcript:\n" + transcript
    )
    return gemini_response


def clean_ai_response(gemini_response):
    """
    Cleans and parses the Gemini API response to extract valid JSON content.
    """
    cleaned_response = re.sub(r'^[^{]*', '', gemini_response)
    cleaned_response = cleaned_response.replace("`", "")
    cleaned_response = cleaned_response.strip()
    gemini_reponse_json = json.loads(cleaned_response)
    return gemini_reponse_json
# endregion
