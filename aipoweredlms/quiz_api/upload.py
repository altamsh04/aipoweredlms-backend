import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_file_to_s3(file_obj, bucket_name=None, object_name=None):
    """
    Upload a file to an S3 bucket
    
    Parameters:
    - file_obj: File object to upload
    - bucket_name: S3 bucket name (defaults to env variable)
    - object_name: S3 object name (defaults to original filename)
    
    Returns:
    - True if file was uploaded, else False
    """
    # Get credentials from environment variables
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    default_bucket = os.getenv('AWS_BUCKET_NAME')

    # Use default bucket if none specified
    if bucket_name is None:
        bucket_name = default_bucket

    # Always upload to /pdfs folder
    object_name = f"pdfs/{file_obj.name}"

    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    try:
        # Upload file
        s3_client.upload_fileobj(file_obj, bucket_name, object_name)
        
        # Generate URL for the uploaded file
        url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return {
            'status': True,
            'url': url,
            'message': 'File uploaded successfully'
        }
    except ClientError as e:
        return {
            'status': False,
            'error': str(e),
            'message': 'Failed to upload file'
        }
