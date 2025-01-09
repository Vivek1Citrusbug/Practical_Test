import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import httpx
from passlib.context import CryptContext
from config import (
    ALGORITHM,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_TOKEN_URL,
    SECRET_KEY,
    SENDGRID_API_KEY,
    FROM_EMAIL,
    EMAIL_HOST_PASSWORD,
    SENDGRID_TEMPLATE_ID,
    RESET_LINK,
)
from apps.user.dependency import verify_password, get_password_hash, create_reset_token,verify_reset_token
import jwt
from database import SessionDep
from fastapi import Depends
from typing import Annotated
from database import Session
from apps.user.application.schemas import UserCreateModel
from apps.user.domain.models import Users
from sqlmodel import SQLModel, select
from database import engine
from apps.user.application.schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context

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


async def save_user_to_db(user_data, session: SessionDep):
    """
    Function to save user data to github user database
    """

    existing_user = session.query(Users).filter_by(email=user_data.get("email")).first()

    if existing_user:
        print(f"User with email:{user_data['email']} already exists in the database.")
    else:
        name_list = user_data["name"].split()
        print(name_list)
        user = Users(
            username=user_data["login"],
            email=user_data.get("email"),
            name=user_data["name"],
            password="",
            first_name=name_list[0],
            last_name=name_list[1],
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


async def register_user_instance(user_data: UserCreateModel, session: Session):
    """
    Domain layer service for registering user
    """

    hashed_password = get_password_hash(user_data.password)
    user_data = user_data.model_dump()
    user_data["password"] = hashed_password
    UserDatabase = Users.model_validate(user_data)
    session.add(UserDatabase)
    session.commit()
    session.refresh(UserDatabase)

    return UserDatabase


async def github_callback_instance(code: str, session: SessionDep):
    """
    Domain layer service for Github callback service
    """

    token_url = GITHUB_TOKEN_URL
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=payload, headers=headers)
        token_data = token_response.json()
        if "access_token" not in token_data:
            raise HTTPException(
                status_code=400, detail="Failed to retrieve access token"
            )

        access_token = token_data["access_token"]

    user_url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        user_response = await client.get(user_url, headers=headers)
        user_data = user_response.json()
        await save_user_to_db(user_data, session)

    jwt_token = create_access_token(
        {"username": user_data["login"], "sub": user_data["id"]}
    )
    return {"jwt_token": jwt_token, "user": user_data}


def mail_service(to_email: str, reset_link: str, session: SessionDep):
    """
    Service for sending email using sendgrid api client.
    """
    user: Users = session.query(Users).filter_by(email=to_email).first()
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
    )
    message.dynamic_template_data = {
        "username": user.username,
        "reset_link": reset_link,
    }
    message.template_id = SENDGRID_TEMPLATE_ID
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    try:
        response = sg.send(message)
        print("Email sent successfully!")
        print(f"Response status code: {response.status_code}")
        return 1
    except Exception as e:
        print(f"Error sending email: {e}")


async def password_reset_instance(session: SessionDep, current_user: Users):
    """
    Service for Creating reset password token
    """

    token = create_reset_token(current_user.email)
    current_user.password_reset_token = token
    reset_link = RESET_LINK + token
    session.add(current_user)
    session.commit()
    reset_link = RESET_LINK + token

    if mail_service(current_user.email, reset_link, session):
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(status_code=500, detail="Error sending email")

async def password_reset_confirm_instance(new_password:str,session: SessionDep, current_user: Users):
    """
    Service for Creating reset password token
    """

    email = verify_reset_token(current_user.password_reset_token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    current_user.password = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password has been reset successfully"}