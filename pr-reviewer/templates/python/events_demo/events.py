# s3_client/events.py

# snippet-start:[s3.event_handler.add_default_bucket]
def add_default_bucket(params, **kwargs):
    """Automatically adds a default bucket if none is provided."""
    if 'Bucket' not in params:
        params['Bucket'] = 'my-default-bucket'
# snippet-end:[s3.event_handler.add_default_bucket]

# snippet-start:[s3.event_handler.log_request]
def log_request(params, **kwargs):
    """Logs the request details."""
    headers = params.get('headers', {})
    print(f"Logging request headers: {headers}")
# snippet-end:[s3.event_handler.log_request]

# snippet-start:[s3.event_handler.add_custom_header]
def add_custom_header(params, **kwargs):
    """Adds a custom header to the request."""
    if 'headers' not in params:
        params['headers'] = {}
    params['headers']['X-Custom-Header'] = 'CustomValue'
    print("Custom header added.")
# snippet-end:[s3.event_handler.add_custom_header]

# snippet-start:[s3.event_handler.log_errors]
def log_errors(exception, **kwargs):
    """Logs any errors that occur during the API call."""
    if exception:
        print(f"Logging error: {exception}")
# snippet-end:[s3.event_handler.log_errors]

# snippet-start:[s3.event_handler.custom_retry_logic]
def custom_retry_logic(response, **kwargs):
    """Implements custom retry logic for server errors."""
    status_code = response[0].status_code
    if status_code == 500:  # Retry on server error
        print("Server error detected, retrying...")
        return 2  # Retry after 2 seconds
    return None
# snippet-end:[s3.event_handler.custom_retry_logic]

