from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from config import ALGORITHM, SECRET_KEY
from apps.user.dependency import verify_password
import jwt
from database import SessionDep
from fastapi import Depends
from typing import Annotated
from database import Session
from apps.user.domain.models import Users
from sqlmodel import SQLModel, select
from database import engine
from apps.user.application.schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def create_db_and_tables():
    """
    Creating database tables
    """

    print("#### Database Created ####")
    SQLModel.metadata.create_all(engine)


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


async def save_user_to_db(user_data):
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
            name=user_data["name"],
        )
        session.add(user)
        session.commit()
        print(f"User {user_data['login']} saved to the database.")
    session.close()


def get_user(session: SessionDep, username: str):
    """
    Function to get user from given username
    """

    statement = select(Users).where(Users.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)], session: SessionDep
):
    """
    Function to get current logged in user
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    """
    Function to get current active user
    """

    return current_user
