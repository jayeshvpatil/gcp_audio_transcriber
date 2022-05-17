from __future__ import unicode_literals, print_function
from google.cloud import speech
from google.cloud import storage
import ffmpeg
import sys

bucket_name = "jvp_test"
prefix = "gs://"


def process_audio(in_filename):
    try:
        out, err = (
            ffmpeg.input(in_filename)
            .output("processed.pcm", format="s16le", acodec="pcm_s16le", ac=1, ar="16k")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    return out


def upload_gcs(processed_audio):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("processed_file.pcm")
    blob.upload_from_filename("processed.pcm")
    gcs_uri = prefix + bucket_name + "/" + blob.name
    print(gcs_uri)
    return gcs_uri
    print(f"File uploaded")


def get_transcripts(audio_uri):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=audio_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)
    return response


def transcribe(in_filename):
    processed_audio = process_audio(in_filename)
    gcs_uri = upload_gcs(processed_audio)
    # gcs_uri = "gs://jvp_test/processed_file.pcm"
    transcripts = get_transcripts(gcs_uri)

    for result in transcripts.results:
        # The first alternative is the most likely one for this portion.
        print("Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))


transcribe("test.wav")
# decode_audio("test.wav")

