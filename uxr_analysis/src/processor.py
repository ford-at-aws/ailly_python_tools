import json
import logging
import os

import boto3

from .config_manager import ConfigManager

# Initialize the S3 client
s3_client = boto3.client("s3")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, output_dir):
        self.output_dir = output_dir  # New parameter for output directory
        self.config_data = ConfigManager.load_config(output_dir)
        self.bucket_name = self.config_data["bucket_name"]
        self.completed_prefix = "transcriptions/completed/"
        self.download_directory = (
            os.path.join(output_dir, "transcripts/")  # Directory for raw downloaded transcriptions
        )
        self.parsed_directory = (
            os.path.join(output_dir, "parsed_transcriptions/")  # Directory for parsed transcriptions
        )

    def print_banner(self):
        """Print a flashy banner."""
        banner = """
        ================================
          UXR Analysis - Process Transcripts
        ================================
        """
        print(banner)

    def list_s3_objects(self):
        """List all objects in an S3 bucket with the specified prefix."""
        try:
            response = s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=self.completed_prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logger.error(f"Error listing objects in bucket {self.bucket_name}: {e}")
            raise

    def download_s3_object(self, key, download_path):
        """Download an S3 object to a local file."""
        if not os.path.exists(os.path.dirname(download_path)):
            os.makedirs(os.path.dirname(download_path))
        try:
            s3_client.download_file(self.bucket_name, key, download_path)
            logger.info(f"Downloaded {key} to {download_path}")
        except Exception as e:
            logger.error(f"Error downloading {key}: {e}")
            raise

    def parse_transcript(self, input_path, output_path):
        """Parse the transcript from the JSON file and save to a new file."""
        try:
            with open(input_path, "r") as f:
                data = json.load(f)
                transcripts = data.get("results", {}).get("transcripts", [])
                transcript_text = " ".join(
                    [t.get("transcript", "") for t in transcripts]
                )

            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path))

            with open(output_path, "w") as f:
                f.write(transcript_text)
            logger.info(f"Parsed transcript saved to {output_path}")
        except Exception as e:
            logger.error(f"Error parsing transcript {input_path}: {e}")
            raise

    def process_transcripts(self):
        """Download and parse transcripts from S3."""
        self.print_banner()

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        if not os.path.exists(self.parsed_directory):
            os.makedirs(self.parsed_directory)

        objects_to_download = self.list_s3_objects()

        for obj_key in objects_to_download:
            if obj_key.endswith(".json"):
                download_path = os.path.join(
                    self.download_directory, os.path.basename(obj_key)
                )
                parsed_path = os.path.join(
                    self.parsed_directory, os.path.basename(obj_key)
                )
                try:
                    self.download_s3_object(obj_key, download_path)
                    self.parse_transcript(download_path, parsed_path)
                except Exception as e:
                    logger.error(f"Error processing object {obj_key}: {e}")
            else:
                logger.info(f"Skipping non-json file: {obj_key}")
        print("✅ Done!")
