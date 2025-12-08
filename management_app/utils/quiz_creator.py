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

    QuizQuestion.objects.create(
        quiz=quiz,
        question_title=gemini_response_json["question"],
        question_options=gemini_response_json["answers"],
        answer=gemini_response_json["correct_answer"]
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


def get_ai_response(transcript: str):
    """
    Generates quiz content using the Gemini API based on the provided transcript.
    """
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
