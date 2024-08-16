import boto3
import time
import uuid
import re

# Initialize the S3 and Transcribe clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

# Specify the bucket and prefixes
bucket_name = '0-fordsbucket'
input_prefix = 'transcriptions/'
output_prefix = 'transcriptions/completed/'

def list_s3_objects(bucket, prefix):
    """List all objects in an S3 bucket with the specified prefix."""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', [])]

def sanitize_s3_key(key):
    """Sanitize S3 key to meet AWS Transcribe requirements."""
    return re.sub(r"[^a-zA-Z0-9-_.!*'()/]", "_", key)

def start_transcribe_job(media_uri, output_bucket, output_key):
    """Start an AWS Transcribe job."""
    job_name = f"transcription-{uuid.uuid4()}"
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat='mp4',  # Change if your media files have a different format
        LanguageCode='en-US',  # Change to your target language code
        OutputBucketName=output_bucket,
        OutputKey=output_key
    )
    return response

def main():
    # List all objects in the specified S3 bucket and prefix
    objects_to_transcribe = list_s3_objects(bucket_name, input_prefix)
    
    for obj_key in objects_to_transcribe:
        if obj_key.endswith('.mp4'):
            media_uri = f"s3://{bucket_name}/{obj_key}"
            sanitized_key = sanitize_s3_key(obj_key.split('/')[-1].replace('.mp4', '.json'))
            output_key = f"{output_prefix}{sanitized_key}"
            response = start_transcribe_job(media_uri, bucket_name, output_key)
            print(f"Started transcription job for {obj_key}, job name: {response['TranscriptionJob']['TranscriptionJobName']}")
            # Optional: sleep to avoid hitting API rate limits
            time.sleep(1)
        else:
            print(f"Skipping non-mp4 file: {obj_key}")

if __name__ == "__main__":
    main()

