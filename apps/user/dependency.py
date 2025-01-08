import jwt
from sqlmodel import SQLModel, select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from apps.user.application.schemas import TokenData
from apps.user.domain.models import Users
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from typing import Annotated, Union
from jwt.exceptions import InvalidTokenError
from datetime import UTC

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
