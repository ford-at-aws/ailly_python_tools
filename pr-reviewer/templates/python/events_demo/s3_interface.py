# s3_client/s3_interface.py

import boto3
from events import (
    add_default_bucket,
    log_request,
    add_custom_header,
    log_errors,
    custom_retry_logic
)

class S3Interface:
    """
    A simple interface for interacting with Amazon S3 using Boto3.

    Methods
    -------
    list_buckets() -> None
        Lists all S3 buckets in the account.

    list_objects(bucket_name: str = None) -> None
        Lists all objects in a specified S3 bucket.

    put_object(bucket_name: str, key: str, body: str) -> None
        Uploads an object to the specified S3 bucket.

    """
    def __init__(self):
        """
        Initializes the S3 client and registers event handlers.
        """
        self.s3 = boto3.client('s3')
        self._register_events()

    def _register_events(self):
        """
        Registers event handlers for S3 operations.
        """
        event_system = self.s3.meta.events

        # snippet-start:[s3.event.add_default_bucket]
        event_system.register('provide-client-params.s3.ListObjectsV2', add_default_bucket)
        # snippet-end:[s3.event.add_default_bucket]

        # snippet-start:[s3.event.log_request]
        event_system.register('before-call.s3.ListBuckets', log_request)
        # snippet-end:[s3.event.log_request]

        # snippet-start:[s3.event.add_custom_header]
        event_system.register('before-call.s3.ListBuckets', add_custom_header)
        # snippet-end:[s3.event.add_custom_header]

        # snippet-start:[s3.event.log_errors]
        event_system.register('after-call-error.s3.ListBuckets', log_errors)
        # snippet-end:[s3.event.log_errors]

        # snippet-start:[s3.event.custom_retry_logic]
        event_system.register('needs-retry.s3.ListBuckets', custom_retry_logic)
        # snippet-end:[s3.event.custom_retry_logic]

    # snippet-start:[s3.method.list_buckets]
    def list_buckets(self):
        """
        Lists all S3 buckets in the account.

        Prints
        ------
        List of bucket names if successful.
        Error message if the operation fails.

        See Also
        --------
        AWS Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_buckets
        """
        try:
            response = self.s3.list_buckets()
            print("Buckets:", [bucket['Name'] for bucket in response.get('Buckets', [])])
        except Exception as e:
            print(f"Failed to list buckets: {e}")
    # snippet-end:[s3.method.list_buckets]

    # snippet-start:[s3.method.list_objects]
    def list_objects(self, bucket_name=None):
        """
        Lists all objects in a specified S3 bucket.

        Parameters
        ----------
        bucket_name : str, optional
            The name of the bucket to list objects from.

        Prints
        ------
        List of object keys in the specified bucket if successful.
        Error message if the operation fails.

        See Also
        --------
        AWS Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2
        """
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            contents = response.get('Contents', [])
            print(f"Objects in {bucket_name}:", [obj['Key'] for obj in contents])
        except Exception as e:
            print(f"Failed to list objects in {bucket_name}: {e}")
    # snippet-end:[s3.method.list_objects]

    # snippet-start:[s3.method.put_object]
    def put_object(self, bucket_name, key, body):
        """
        Uploads an object to the specified S3 bucket.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to upload the object to.
        key : str
            The key (name) for the uploaded object.
        body : str
            The content to be uploaded as the object.

        Prints
        ------
        Success message with response details if successful.
        Error message if the operation fails.

        See Also
        --------
        AWS Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object
        """
        try:
            response = self.s3.put_object(Bucket=bucket_name, Key=key, Body=body)
            print(f"Uploaded {key} to {bucket_name}. Response: {response}")
        except Exception as e:
            print(f"Failed to upload {key} to {bucket_name}: {e}")
    # snippet-end:[s3.method.put_object]

