import logging
import os
import re
import json
import time
import uuid
import shutil
from datetime import datetime

import boto3
from tabulate import tabulate

from .config_manager import ConfigManager
from .utils import wait_for_s3_upload

# Initialize the S3 and Transcribe clients
s3_client = boto3.client("s3")
transcribe_client = boto3.client("transcribe")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Uploader:
    def __init__(self, directory, output_dir):
        self.directory = directory
        self.output_dir = output_dir  # New parameter for output directory
        self.config_data = {}
        self.config_file = os.path.join(output_dir, "uxr_config.json")

    def print_banner(self, banner_text):
        """Print a banner."""
        banner = f"""
        ===============================
          {banner_text}
        ===============================
        """
        print(banner)

    def create_s3_bucket(self, bucket_name):
        """Create an S3 bucket."""
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} created")
            self.config_data["bucket_name"] = bucket_name
            ConfigManager.save_config(self.config_data, self.output_dir)
        except s3_client.exceptions.BucketAlreadyExists:
            logger.warning(f"Bucket {bucket_name} already exists")
        except Exception as e:
            logger.error(f"Error creating bucket: {e}")
            raise

    def upload_file_to_s3(self, bucket_name, file_path, object_name=None):
        """Upload a file to an S3 bucket."""
        if object_name is None:
            object_name = os.path.basename(file_path)
        start_time = time.time()
        try:
            logger.info(f"Upload - STARTING - {bucket_name}/{object_name}")
            s3_client.upload_file(file_path, bucket_name, object_name)
            wait_for_s3_upload(bucket_name, object_name)
            elapsed_time = time.time() - start_time
            logger.info(
                f"Upload - COMPLETE - {bucket_name}/{object_name} in {elapsed_time:.2f} seconds"
            )
            return elapsed_time
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            raise

    def list_files(self):
        """List all mp4 files in the directory with their sizes."""
        files = []
        for file_name in os.listdir(self.directory):
            if file_name.endswith(".mp4"):
                file_path = os.path.join(self.directory, file_name)
                file_size = os.path.getsize(file_path)
                files.append((file_name, file_size))
        return files

    def estimate_transcription_time(self, file_size):
        """Estimate the transcription time based on file size."""
        # Transcription time is 1.5 seconds per MB
        return (file_size / (1024 * 1024)) * 1.5  # 1.5 seconds per MB

    def sanitize_s3_key(self, key):
        """Sanitize S3 key to meet AWS Transcribe requirements."""
        return re.sub(r"[^a-zA-Z0-9-_.!*'()/]", "_", key)

    def start_transcription_job(self, media_uri, output_bucket, output_key):
        """Start an AWS Transcribe job."""
        job_name = f"transcription-{uuid.uuid4()}"
        try:
            response = transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": media_uri},
                MediaFormat="mp4",
                LanguageCode="en-US",
                OutputBucketName=output_bucket,
                OutputKey=output_key,
            )
            logger.info(
                f"Started transcription job for {media_uri}, job name: {response['TranscriptionJob']['TranscriptionJobName']}"
            )
            return response
        except Exception as e:
            logger.error(f"Error starting transcription job for {media_uri}: {e}")
            raise

    def confirm_proceed(self, files):
        """Ask the user to confirm if they want to proceed."""
        headers = ["File Name", "Size (MB)", "Estimated Transcription Time (min)"]
        table = [
            (
                file_name,
                f"{file_size / (1024 * 1024):.2f}",
                f"{self.estimate_transcription_time(file_size) / 60:.2f}",
            )
            for file_name, file_size in files
        ]
        print(tabulate(table, headers, tablefmt="grid"))

        confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        return confirm == "yes"

    def check_previous_run(self):
        """Check for a previous run and prompt the user to reuse the same bucket."""
        try:
            self.config_data = ConfigManager.load_config(self.output_dir)
            previous_bucket = self.config_data.get("bucket_name")
            if previous_bucket:
                print(f"Previous S3 bucket found: {previous_bucket}")
                use_previous = (
                    input("Do you want to use the same bucket? (yes/no): ")
                    .strip()
                    .lower()
                )
                if use_previous == "yes":
                    return previous_bucket
                else:
                    # Delete the results directory and reset config data if the user wants to create a new bucket
                    results_dir = os.path.join(self.output_dir, 'results')
                    if os.path.exists(results_dir):
                        shutil.rmtree(results_dir)
                        print(f"Deleted existing results directory: {results_dir}")

                    self.config_data = {}
                    ConfigManager.save_config(self.config_data, self.output_dir)
                    return None
        except Exception:
            pass
        return None

    def upload_videos(self):
        """Upload videos from a directory to S3 and start transcription jobs."""
        self.print_banner("UXR Analysis - Video Upload")

        bucket_name = self.check_previous_run()
        if not bucket_name:
            bucket_name = input("Please enter a name for the S3 bucket: ").strip()
            self.create_s3_bucket(bucket_name)

        files = self.list_files()

        if not self.confirm_proceed(files):
            logger.info("Operation cancelled by user.")
            return

        if "files" not in self.config_data:
            self.config_data["files"] = []

        existing_files = {file["file_name"] for file in self.config_data["files"] if "upload_time" in file}

        self.print_banner("Uploading Videos to S3")
        uploaded_files = []
        # Upload all files to S3 in batch
        for file_name, file_size in files:
            if bucket_name not in self.config_data.get("bucket_name", "") or file_name not in existing_files:
                file_path = os.path.join(self.directory, file_name)
                try:
                    upload_time = self.upload_file_to_s3(
                        bucket_name, file_path, f"transcriptions/{file_name}"
                    )
                    media_uri = f"s3://{bucket_name}/transcriptions/{file_name}"
                    sanitized_key = self.sanitize_s3_key(file_name.replace(".mp4", ".json"))
                    output_key = f"transcriptions/completed/{sanitized_key}"

                    file_info = {
                        "file_name": file_name,
                        "file_size": file_size,
                        "media_uri": media_uri,
                        "output_key": output_key,
                        "upload_time": upload_time,
                    }
                    self.config_data["files"].append(file_info)
                    ConfigManager.save_config(self.config_data, self.output_dir)

                    uploaded_files.append(file_info)

                    # Report progress to user
                    logger.info(
                        f"Uploaded {file_name} ({file_size / (1024 * 1024):.2f} MB) in {upload_time:.2f} seconds"
                    )

                except Exception as e:
                    logger.error(f"Error uploading file {file_name}: {e}")
            else:
                logger.info(f"Skipping already uploaded file: {file_name}")

        if uploaded_files:
            headers = ["S3 Key", "URI", "Size (MB)", "Upload Time (s)"]
            table = [
                (
                    file_info["file_name"],
                    file_info["media_uri"],
                    f"{file_info['file_size'] / (1024 * 1024):.2f}",
                    f"{file_info['upload_time']:.2f}",
                )
                for file_info in uploaded_files
            ]
            print("\nSummary of Uploaded Files:\n")
            print(tabulate(table, headers, tablefmt="grid"))

        self.print_banner("Starting Transcription Jobs")
        # Start transcription jobs for all files
        for file_info in self.config_data["files"]:
            if "job_name" in file_info:
                logger.info(
                    f"Skipping already started transcription job for file: {file_info['file_name']}"
                )
                continue

            try:
                job_response = self.start_transcription_job(
                    file_info["media_uri"], bucket_name, file_info["output_key"]
                )
                file_info["job_name"] = job_response["TranscriptionJob"][
                    "TranscriptionJobName"
                ]
                file_info["start_time"] = job_response["TranscriptionJob"][
                    "CreationTime"
                ].isoformat()  # Convert datetime to ISO format string
                ConfigManager.save_config(self.config_data, self.output_dir)
                time.sleep(1)  # Optional: sleep to avoid hitting API rate limits
            except Exception as e:
                logger.error(
                    f"Error starting transcription job for {file_info['file_name']}: {e}"
                )

        # Pretty print the summary of uploaded files and transcription jobs
        headers = [
            "Uploaded File",
            "Transcription Job",
            "Destination Location",
            "Upload Time (s)",
        ]
        table = [
            (
                file_info["file_name"],
                file_info.get("job_name", "Pending"),
                file_info["output_key"],
                f"{file_info['upload_time']:.2f}",
            )
            for file_info in self.config_data["files"]
        ]
        print("\nSummary of Uploaded Files and Transcription Jobs:\n")
        print(tabulate(table, headers, tablefmt="grid"))

        # Provide URL to AWS Transcribe Console
        region = boto3.Session().region_name
        transcribe_console_url = f"https://{region}.console.aws.amazon.com/transcribe/home?region={region}#jobs"
        print(f"\nYou can view your transcription jobs here: {transcribe_console_url}")

    # Initialize boto3 client for Transcribe
    transcribe = boto3.client('transcribe')
