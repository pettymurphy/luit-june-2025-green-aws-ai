import boto3

polly = boto3.client('polly')
response = polly.describe_voices()

for voice in response['Voices']:
    print(voice['Name'], '-', voice['LanguageName'])
