import boto3
import os
import time
import json
from pathlib import Path
import sys

# Get ENV variables
ENV_PREFIX = os.getenv('ENV_PREFIX', 'beta')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET = os.getenv('S3_BUCKET')

# Input validation
if len(sys.argv) != 2:
    print("Usage: python process_audio_multilang.py <path_to_audio_file>")
    sys.exit(1)

local_audio_path = sys.argv[1]
filename = Path(local_audio_path).stem

# Upload original audio to S3
s3_client = boto3.client('s3', region_name=AWS_REGION)
s3_key_input = f"{ENV_PREFIX}/audio_inputs/{filename}.mp3"

try:
    s3_client.upload_file(local_audio_path, S3_BUCKET, s3_key_input)
    print(f"Uploaded {local_audio_path} to s3://{S3_BUCKET}/{s3_key_input}")
except Exception as e:
    print(f"Error uploading audio: {e}")
    sys.exit(1)

# Transcription setup
transcribe = boto3.client('transcribe', region_name=AWS_REGION)
job_name = f"transcribe-{filename}-{int(time.time())}"
media_uri = f"s3://{S3_BUCKET}/{s3_key_input}"

try:
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat='mp3',
        LanguageCode='en-US',
        OutputBucketName=S3_BUCKET,
        OutputKey=f"{ENV_PREFIX}/transcripts/"
    )
    print("Waiting for transcription...")
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if status == 'FAILED':
        print("Transcription failed.")
        sys.exit(1)

    transcript_s3_key = f"{ENV_PREFIX}/transcripts/{job_name}.json"
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key=transcript_s3_key)
    transcript_json = json.loads(obj['Body'].read())
    transcript_text = transcript_json['results']['transcripts'][0]['transcript']
    print("Transcription complete.")

    # Save raw transcript to S3
    raw_key = f"{ENV_PREFIX}/transcripts/{filename}.txt"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=raw_key,
        Body=transcript_text.encode('utf-8')
    )
    print(f"Saved raw transcript to s3://{S3_BUCKET}/{raw_key}")
except Exception as e:
    print(f"Error during transcription: {e}")
    sys.exit(1)

# Language + Voice configuration
languages = {
    'es': 'Miguel',     # Spanish
    'fr': 'Mathieu'     # French
}

translate = boto3.client('translate', region_name=AWS_REGION)
polly = boto3.client('polly', region_name=AWS_REGION)

for lang_code, voice_id in languages.items():
    print(f"Processing language: {lang_code} with voice: {voice_id}")

    try:
        translation = translate.translate_text(
            Text=transcript_text,
            SourceLanguageCode='en',
            TargetLanguageCode=lang_code
        )
        translated_text = translation['TranslatedText']
        print(f"Translation to {lang_code} complete.")
    except Exception as e:
        print(f"Translation to {lang_code} failed: {e}")
        continue

    # Save translated text to S3
    translated_key = f"{ENV_PREFIX}/translations/{filename}_{lang_code}.txt"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=translated_key,
            Body=translated_text.encode('utf-8')
        )
        print(f"Saved translated text to s3://{S3_BUCKET}/{translated_key}")
    except Exception as e:
        print(f"Failed to save translation: {e}")
        continue

    # Synthesize translated text
    try:
        polly_response = polly.synthesize_speech(
            Text=translated_text,
            OutputFormat='mp3',
            VoiceId=voice_id
        )
        audio_output = polly_response['AudioStream'].read()
        audio_key = f"{ENV_PREFIX}/audio_outputs/{filename}_{lang_code}.mp3"

        s3_client.put_object(Bucket=S3_BUCKET, Key=audio_key, Body=audio_output)
        print(f"Uploaded audio to s3://{S3_BUCKET}/{audio_key}")
    except Exception as e:
        print(f"Polly synthesis failed for {lang_code}: {e}")


