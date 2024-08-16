import boto3
import os
import json

# Initialize the S3 client
s3_client = boto3.client('s3')

# Specify the bucket and prefixes
bucket_name = '0-fordsbucket'
completed_prefix = 'transcriptions/completed/'
download_directory = './transcripts/'  # Directory for raw downloaded transcriptions
parsed_directory = './parsed_transcriptions/'  # Directory for parsed transcriptions

def list_s3_objects(bucket, prefix):
    """List all objects in an S3 bucket with the specified prefix."""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', [])]

def download_s3_object(bucket, key, download_path):
    """Download an S3 object to a local file."""
    if not os.path.exists(os.path.dirname(download_path)):
        os.makedirs(os.path.dirname(download_path))
    s3_client.download_file(bucket, key, download_path)
    print(f"Downloaded {key} to {download_path}")

def parse_transcript(input_path, output_path):
    """Parse the transcript from the JSON file and save to a new file."""
    with open(input_path, 'r') as f:
        data = json.load(f)
        transcripts = data.get('results', {}).get('transcripts', [])
        transcript_text = ' '.join([t.get('transcript', '') for t in transcripts])
    
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    
    with open(output_path, 'w') as f:
        f.write(transcript_text)
    print(f"Parsed transcript saved to {output_path}")

def main():
    # List all objects in the specified S3 bucket and prefix
    objects_to_download = list_s3_objects(bucket_name, completed_prefix)
    
    for obj_key in objects_to_download:
        if obj_key.endswith('.json'):
            download_path = os.path.join(download_directory, obj_key.split('/')[-1])
            download_s3_object(bucket_name, obj_key, download_path)
            
            # Parse the transcript and save to a new file
            parsed_path = os.path.join(parsed_directory, obj_key.split('/')[-1])
            parse_transcript(download_path, parsed_path)
        else:
            print(f"Skipping non-json file: {obj_key}")

if __name__ == "__main__":
    # Ensure the directories exist
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    if not os.path.exists(parsed_directory):
        os.makedirs(parsed_directory)
    
    main()

