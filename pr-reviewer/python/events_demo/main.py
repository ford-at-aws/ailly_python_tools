# s3_client/main.py

from s3_interface import S3Interface

def main():
    """
    Demonstrates basic S3 operations using the S3Interface.
    """
    s3_client = S3Interface()

    # snippet-start:[s3.main.list_buckets]
    # Listing buckets
    s3_client.list_buckets()
    # snippet-end:[s3.main.list_buckets]

    # snippet-start:[s3.main.list_objects]
    # Listing objects in a specific bucket
    s3_client.list_objects(bucket_name='my-default-bucket')
    # snippet-end:[s3.main.list_objects]

    # snippet-start:[s3.main.put_object]
    # Uploading an object
    s3_client.put_object(bucket_name='my-default-bucket', key='example.txt', body='Hello, world!')
    # snippet-end:[s3.main.put_object]

if __name__ == "__main__":
    main()

