import logging
import time

import boto3

logger = logging.getLogger(__name__)


def wait_for_s3_upload(bucket_name, object_name):
    """Wait for an S3 upload to complete, providing feedback to the user."""
    s3 = boto3.client("s3")
    while True:
        try:
            s3.head_object(Bucket=bucket_name, Key=object_name)
            # If head_object is successful, the upload is done
            return
        except s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # Object not yet uploaded
                pass
            else:
                logger.error(f"Error checking upload status for {object_name}: {e}")
                break

        # Print feedback to the user
        print("\r.")
        time.sleep(1)  # Wait for 1 second before checking again
