# Polly Audio Synthesizer Automation

This project automates the conversion of text to speech using **Amazon Polly** and uploads the audio to **Amazon S3**, triggered by GitHub Actions.

---

## 🔧 How It Works

- `synthesize.py` reads text from `speech.txt`
- Synthesizes it into `speech.mp3` using Polly
- Uploads to your S3 bucket under:
  - `polly-audio/beta.mp3` (on Pull Request)
  - `polly-audio/prod.mp3` (on merge to `main`)

---

## 🔐 Setup Instructions

### 1. Add GitHub Secrets
Go to your repo → Settings → Secrets → `Actions`:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g. `us-east-1`)

### 2. S3 Bucket Setup
Create a bucket (e.g. `green-bucket-s3-feb`) and folder `polly-audio/`  
Assign IAM permissions like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PollyReadUpload",
      "Effect": "Allow",
      "Action": [
        "polly:SynthesizeSpeech",
        "polly:DescribeVoices",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}

# Multilingual Audio Processing Pipeline (AWS Transcribe + Translate + Polly)

This project automates the transcription, translation, and text-to-speech synthesis of uploaded `.mp3` audio using AWS AI services. It processes one audio input and produces multiple language outputs using **Amazon Transcribe**, **Amazon Translate**, and **Amazon Polly**, all triggered via GitHub Actions.

---

## 🔧 How It Works

- A `.mp3` file is passed to `process_audio.py`
- The script:
  - Uploads the audio to your S3 bucket under:  
    `beta/audio_inputs/filename.mp3` or `prod/audio_inputs/filename.mp3`
  - Transcribes speech to text using **Amazon Transcribe**
  - Translates the transcript to multiple languages (e.g. Spanish, French)
  - Synthesizes translated speech using **Amazon Polly**
    - Uses:
      - `Miguel` for Spanish
      - `Mathieu` for French
      - `Joey` for English
  - Uploads:
    - Raw transcript: `transcripts/filename.txt`
    - JSON transcript output: `transcripts/transcribe-job-id.json`
    - Translations: `translations/filename_es.txt`, `filename_fr.txt`
    - Audio output: `audio_outputs/filename_es.mp3`, `filename_fr.mp3`

---

## 🧪 Example Output Structure in S3

multilingual-audio-pipeline/
├── beta/
│ ├── audio_inputs/
│ │ └── test_audio.mp3
│ ├── transcripts/
│ │ ├── test_audio.txt
│ │ └── transcribe-*.json
│ ├── translations/
│ │ ├── test_audio_es.txt
│ │ └── test_audio_fr.txt
│ └── audio_outputs/
│ ├── test_audio_es.mp3
│ └── test_audio_fr.mp3


---

## 🔐 Setup Instructions

### 1. Add GitHub Secrets

Go to your GitHub repo → Settings → Secrets → **Actions** and add:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g. `us-east-1`)
- `S3_BUCKET` (e.g. `multilingual-audio-pipeline`)
- Optional: `ENV_PREFIX` (`beta` or `prod`)

### 2. S3 Bucket Setup

Create a bucket (e.g. `multilingual-audio-pipeline`) and ensure the following folders are created by uploading a dummy file into each:

- `beta/audio_inputs/`
- `beta/audio_outputs/`
- `beta/transcripts/`
- `beta/translations/`

### 3. IAM Permissions

Attach an IAM policy with the following minimum permissions to your GitHub Actions IAM user or role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "FullAIAndS3Access",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob",
        "translate:TranslateText",
        "polly:SynthesizeSpeech",
        "polly:DescribeVoices"
      ],
      "Resource": "*"
    }
  ]
}

| Language | Polly Voice |
| -------- | ----------- |
| English  | Joey        |
| Spanish  | Miguel      |
| French   | Mathieu     |
