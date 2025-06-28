import os
import boto3

region = os.environ['AWS_REGION']
bucket_name = os.environ['S3_BUCKET']
s3_key = os.environ['S3_KEY']

polly = boto3.client('polly', region_name=region)
s3 = boto3.client('s3', region_name=region)

input_file = 'speech.txt'
with open(input_file, 'r') as file:
    text = file.read()

response = polly.synthesize_speech(
    Text=text,
    OutputFormat='mp3',
    VoiceId='Brian'
)

with open('speech.mp3', 'wb') as file:
    file.write(response['AudioStream'].read())
s3.upload_file('speech.mp3', bucket_name, s3_key)

print(f"✅ Uploaded to s3://{bucket_name}/{s3_key}")
