import boto3

polly = boto3.client('polly')
s3 = boto3.client('s3')

#define file and bucket
input_file = 'speech.txt'
bucket_name = 'green-bucket-s3-feb'
s3_key = 'polly-audio/beta.mp3'

# Read text from
with open(input_file, 'r') as file:
    text = file.read()

# Convert text to speech
response = polly.synthesize_speech(
    Text=text,
    OutputFormat= 'mp3',
    VoiceId= 'Brian'
)

# Save and upload the mp3 file
with open('speech.mp3', 'wb') as file:
    file.write(response['AudioStream'].read())

# Upload to s3

s3.upload_file('speech.mp3', bucket_name, s3_key)

print(f"Uploaded to s3://{bucket_name}/{s3_key}")