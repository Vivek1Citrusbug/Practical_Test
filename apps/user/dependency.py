import jwt
from sqlmodel import SQLModel, select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from apps.user.application.schemas import TokenData
from apps.user.domain.models import Users
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from typing import Annotated, Union
from jwt.exceptions import InvalidTokenError
from datetime import UTC, datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    Function o verify password if user
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Function to geet password hashing
    """

    return pwd_context.hash(password)


def create_reset_token(email: str):
    expire = datetime.now(UTC) + timedelta(hours=1)  # Token valid for 1 hour
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
