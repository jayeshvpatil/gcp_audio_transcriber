from __future__ import unicode_literals, print_function
from google.cloud import speech
import ffmpeg
import sys


def decode_audio(in_filename):
    try:
        out, err = (
            ffmpeg.input(in_filename)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar="16k")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return out


def get_transcripts(audio_data):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return [result.alternatives[0].transcript for result in response.results]


def transcribe(in_filename):
    audio_data = decode_audio(in_filename)
    transcripts = get_transcripts(audio_data)
    for transcript in transcripts:
        print(repr(transcript.encode("utf-8")))


transcribe("test.wav")
