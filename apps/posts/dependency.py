import os
import boto3
from botocore.exceptions import NoCredentialsError
from config import (
    MINIO_STORAGE_ENDPOINT,
    MINIO_STORAGE_ACCESS_KEY,
    MINIO_STORAGE_SECRET_KEY,
    MINIO_BUCKET_NAME,
    MINIO_POST_FILE_BUCKET,
)

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_STORAGE_ENDPOINT}",
    aws_access_key_id=MINIO_STORAGE_ACCESS_KEY,
    aws_secret_access_key=MINIO_STORAGE_SECRET_KEY,
)


def upload_to_minio(file: bytes, filename: str):
    try:
        
        s3.put_object(
            Bucket=MINIO_POST_FILE_BUCKET,
            Key=filename,
            Body=file,
            ContentType="application/octet-stream",
        )
        return f"http://{MINIO_STORAGE_ENDPOINT}/{MINIO_POST_FILE_BUCKET}/{filename}"

    except NoCredentialsError:
        return "Credentials not available"
    except Exception as e:
        return f"Error uploading file: {str(e)}"
