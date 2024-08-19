import json
import logging
import os
import time
from datetime import datetime
import boto3
from tabulate import tabulate

from .config_manager import ConfigManager

# Initialize the S3 client
s3_client = boto3.client("s3")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionJobMonitor:
    def __init__(self, output_dir):
        self.output_dir = output_dir  # New parameter for output directory
        self.transcribe = boto3.client('transcribe')
        self.config_file = os.path.join(output_dir, "uxr_config.json")

    @staticmethod
    def read_jobs_from_file(file_path):
        """Read job names, sizes, and start times from a JSON data file."""
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return []

        jobs = []
        with open(file_path, 'r') as file:
            data = json.load(file)
            for item in data.get("files", []):
                job_name = item.get("job_name")
                size_in_mb = item.get("file_size") / (1024 * 1024)  # Convert from bytes to MB
                start_time_str = item.get("start_time")
                try:
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    jobs.append((job_name, size_in_mb, start_time))
                except ValueError:
                    print(f"Invalid time value for job {job_name}.")
        return jobs

    def get_transcription_job_status(self, job_name):
        """Get the status of a transcription job."""
        try:
            response = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = response['TranscriptionJob']['TranscriptionJobStatus']
            return job_status
        except Exception as e:
            print(f"Error fetching status for job {job_name}: {e}")
            return None

    @staticmethod
    def calculate_completion_percentage(job_status, size_in_mb, start_time):
        """Calculate the completion percentage based on job status, size, and start time."""
        if job_status == 'COMPLETED':
            return 100
        elif job_status == 'IN_PROGRESS':
            # Calculate estimated duration based on size
            estimated_duration = size_in_mb * 1.5  # 1.5 seconds per MB
            current_time = time.time()
            elapsed_time = current_time - start_time.timestamp()
            percentage = min((elapsed_time / estimated_duration) * 100, 99)  # Cap at 99%
            return percentage
        elif job_status == 'FAILED':
            return 0
        else:
            return 0

    def report_job_completion(self):
        """Report the completion status of transcription jobs."""
        jobs = self.read_jobs_from_file(self.config_file)
        if not jobs:
            return

        headers = ["Job Name", "Status", "Completion (%)"]
        table = []

        for job_name, size_in_mb, start_time in jobs:
            job_status = self.get_transcription_job_status(job_name)
            if job_status:
                completion_percentage = self.calculate_completion_percentage(job_status, size_in_mb, start_time)
                table.append((job_name, job_status, f"{completion_percentage:.2f}%"))
            else:
                table.append((job_name, "UNKNOWN", "N/A"))

        print(tabulate(table, headers, tablefmt="grid"))
