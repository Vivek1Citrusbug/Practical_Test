import jwt
import os
import boto3
from sqlmodel import SQLModel, select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from apps.user.application.schemas import TokenData
from apps.user.domain.models import Users
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from typing import Annotated, Union
from jwt.exceptions import InvalidTokenError
from datetime import UTC, datetime, timedelta
from botocore.exceptions import NoCredentialsError
from config import (
    MINIO_STORAGE_ENDPOINT,
    MINIO_STORAGE_ACCESS_KEY,
    MINIO_STORAGE_SECRET_KEY,
    MINIO_BUCKET_NAME,
    MINIO_PROFILE_PICTURE_BUCKET,
    MINIO_POST_FILE_BUCKET,
)
from enum import Enum

s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_STORAGE_ENDPOINT}",
    aws_access_key_id=MINIO_STORAGE_ACCESS_KEY,
    aws_secret_access_key=MINIO_STORAGE_SECRET_KEY,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    Function o verify password if user
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Function to get password hashing
    """

    return pwd_context.hash(password)


def create_reset_token(email: str):
    """
    Function to create password reset token
    """

    expire = datetime.now(UTC) + timedelta(hours=1)  # Token valid for 1 hour
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_reset_token(token: str):
    """
    Function to verify password reset token
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def upload_to_minio(file: bytes, filename: str):
    """
    Function to upload file to minio storage bucket
    """

    try:
        s3.put_object(
            Bucket=MINIO_PROFILE_PICTURE_BUCKET,
            Key=filename,
            Body=file,
            ContentType="application/octet-stream",
        )
        return (
            f"http://{MINIO_STORAGE_ENDPOINT}/{MINIO_PROFILE_PICTURE_BUCKET}/{filename}"
        )

    except NoCredentialsError:
        return "Credentials not available"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


def remove_object_from_minio(bucket_name: str, object_name: list):
    """
    Function to delete file from minio storage bucket
    """
    
    delete_objects = []
    for obj_name in object_name:
        delete_objects.append({"Key": obj_name})

    try:
        response = s3.delete_objects(
            Bucket=bucket_name, Delete={"Objects": delete_objects}
        )
        if "Deleted" in response:
            for deleted in response["Deleted"]:
                print(
                    f"Object '{deleted['Key']}' removed successfully from the bucket."
                )
        if "Errors" in response:
            for error in response["Errors"]:
                print(f"Error removing object '{error['Key']}': {error['Message']}")
        else:
            print("Removal completed")
    except Exception as err:
        print(f"Error removing object: {str(err)}")


class ConnectionResponse(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
