import boto3
import sys
import os
from datetime import datetime


# Get AWS Region from environment
region = os.getenv("AWS_REGION")
if not region:
    print("❌ AWS_REGION is not set in the environment.")
    sys.exit(1)

# Initialize AWS clients
s3 = boto3.client("s3", region_name=region)
rekognition = boto3.client("rekognition", region_name=region)
dynamodb = boto3.resource("dynamodb", region_name=region)


# Read command-line arguments
try:
    image_path = sys.argv[1]
    branch = sys.argv[2]
except IndexError:
    print("[ERROR] Missing arguments. Usage: python analyze_image.py <image_path> <branch_name>")
    sys.exit(1)

# Validate image path
if not os.path.exists(image_path):
    print(f"[ERROR] File not found: {image_path}")
    sys.exit(1)

# Get environment variables
try:
    bucket_name = os.environ['S3_BUCKET']
    table_name = os.environ['DYNAMODB_TABLE_BETA'] if 'beta' in branch.lower() else os.environ['DYNAMODB_TABLE_PROD']
except KeyError as e:
    print(f"[ERROR] Missing environment variable: {str(e)}")
    sys.exit(1)

# Generate filename and S3 path
filename = os.path.basename(image_path)
s3_key = f"rekognition-input/{filename}"

# Upload image to S3
try:
    s3.upload_file(image_path, bucket_name, s3_key)
    print(f"[S3] Uploaded {filename} to s3://{bucket_name}/{s3_key}")
except Exception as e:
    print(f"[ERROR] Failed to upload image to S3: {str(e)}")
    sys.exit(1)

# Call Rekognition for label detection
try:
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': s3_key}},
        MaxLabels=10,
        MinConfidence=75
    )
    labels = [
        {"Name": label["Name"], "Confidence": round(label["Confidence"], 2)}
        for label in response['Labels']
    ]
    print(f"[Rekognition] Detected {len(labels)} label(s): {labels}")
except Exception as e:
    print(f"[ERROR] Rekognition failed: {str(e)}")
    sys.exit(1)

# Write results to DynamoDB
try:
    table = dynamodb.Table(table_name)
    table.put_item(Item={
        'filename': s3_key,
        'labels': labels,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'branch': branch
    })
    print(f"[DynamoDB] Successfully logged to table: {table_name}")
except Exception as e:
    print(f"[ERROR] Failed to write to DynamoDB: {str(e)}")
    sys.exit(1)


