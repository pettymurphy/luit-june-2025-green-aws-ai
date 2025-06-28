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
