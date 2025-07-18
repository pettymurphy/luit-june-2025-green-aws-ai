import boto3
import sys
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get AWS Region from environment
region = os.getenv("AWS_REGION")
if not region:
    print("❌ AWS_REGION is not set in the environment.")
    sys.exit(1)

rekognition = boto3.client("rekognition", region_name=region)

# Read command-line arguments
try:
    image_path = sys.argv[1]
    branch = sys.argv[2]
except IndexError:
    print("[ERROR] Missing arguments. Usage: python analyze_image.py <image_path> <branch_name>")
    sys.exit(1)

# Validate image path
if not os.path.exists(image_path):
    print(f"[ERROR] Image path '{image_path}' does not exist.")
    sys.exit(1)

# Upload to S3
bucket = os.getenv("S3_BUCKET")
if not bucket:
    print("❌ S3_BUCKET is not set in the environment.")
    sys.exit(1)

image_name = os.path.basename(image_path)
s3_key = f"rekognition-input/{image_name}"

try:
    s3.upload_file(image_path, bucket, s3_key)
    print(f"[S3] Uploaded {image_name} to s3://{bucket}/{s3_key}")
except Exception as e:
    print(f"[ERROR] Failed to upload to S3: {e}")
    sys.exit(1)

# Detect labels with Rekognition
try:
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': s3_key}},
        MaxLabels=10
    )
    labels = response['Labels']
    print(f"[Rekognition] Detected {len(labels)} label(s): {labels}")
except Exception as e:
    print(f"[ERROR] Rekognition failed: {e}")
    sys.exit(1)

# Convert confidence values to Decimal for DynamoDB
for label in labels:
    label['Confidence'] = Decimal(str(label['Confidence']))

# Select DynamoDB table based on branch
table_name = os.getenv("DYNAMODB_TABLE_BETA") if branch == "rekognition-logging" else os.getenv("DYNAMODB_TABLE_PROD")
if not table_name:
    print(f"[ERROR] No DynamoDB table found for branch '{branch}'")
    sys.exit(1)

table = dynamodb.Table(table_name)
timestamp = datetime.utcnow().isoformat()

# Store results in DynamoDB
try:
    table.put_item(
        Item={
            'Image': image_name,
            'Timestamp': timestamp,
            'Labels': [
                {
                    'Name': label['Name'],
                    'Confidence': label['Confidence']
                } for label in labels
            ]
        }
    )
    print(f"[DynamoDB] Results saved to {table_name}")
except Exception as e:
    print(f"❌ Error: Failed to write to DynamoDB: {e}")
    sys.exit(1)
