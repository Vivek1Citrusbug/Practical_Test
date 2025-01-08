from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from config import ALGORITHM, SECRET_KEY
from apps.user.dependency import get_current_active_user, get_user
import jwt
from database import SessionDep
from fastapi import Depends
from typing import Annotated
from database import Session
from apps.user.domain.models import Users

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


def authenticate_user(session, username: str, password: str):
    """
    Function to authenticate user
    """

    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Function to create access token
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def save_user_to_db(user_data):
    """
    Function to save user data to github user database
    """

    session = Session()
    existing_user = session.query(Users).filter_by(email=user_data["email"]).first()
    if existing_user:
        print(f"User with email:{user_data['email']} already exists in the database.")
    else:
        user = Users(
            username=user_data["login"],
            email=user_data.get("email"),
            name=user_data["name"]
        )
        session.add(user)
        session.commit()
        print(f"User {user_data['login']} saved to the database.")
    session.close()



