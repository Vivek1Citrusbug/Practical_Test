import httpx
from fastapi.responses import RedirectResponse
import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, requests
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, select
from apps.user.domain.models import Users
from apps.user.application.schemas import (
    Token,
    UserBaseModel,
    UserCreateModel,
    UserPublicModel,
    PasswordResetRequest,
)
from fastapi import status
from datetime import datetime, timedelta, timezone
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    GITHUB_AUTHORIZATION_BASE_URL,
    GITHUB_REDIRECT_URI,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_TOKEN_URL,
    GITHUB_API_URL,
    RESET_LINK,
)
from apps.user.application.schemas import (
    UserBaseModel,
    Token,
    TokenData,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine, SessionDep
from jwt.exceptions import InvalidTokenError
from apps.user.dependency import (
    create_reset_token,
    verify_reset_token,
    get_password_hash,
)
from apps.user.domain.service import (
    create_access_token,
    verify_password,
    authenticate_user,
    get_user,
    get_current_user,
    get_current_active_user,
    github_callback_instance,
    mail_service,
)
from database import Session
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
from apps.user.application.service import register_user, github_callback_application

router = APIRouter()


# User registration endpoint
@router.post("/register", response_model=UserPublicModel)
async def register(user: UserCreateModel, session: SessionDep):
    """
    Function to create user based on the allowed roles
    """
    return await register_user(user, session)


@router.post(
    "/token",
    status_code=status.HTTP_201_CREATED,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    """
    Function to login user and return access token in return
    """

    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/github/login")
def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=read:user,user:email"
    )
    return {"auth_url": github_auth_url}


@router.get("/github/callback")
async def github_callback(code: str, session: SessionDep):
    return await github_callback_application(code, session)


@router.post("/password-reset/")
def password_reset_request(
    data: PasswordResetRequest,
    session: SessionDep,
):
    user: Users = session.query(Users).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(user.email)
    user.password_reset_token = token

    session.add(user)
    session.commit()
    reset_link = RESET_LINK + token
    print(reset_link)

    if mail_service(user.email, session):
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(status_code=500, detail="Error sending email")


@router.post("/password-reset/confirm/")
def password_reset_confirm(email: str, new_password: str, session: SessionDep):
    user: Users = session.query(Users).filter_by(email=email).first()
    email = verify_reset_token(user.password_reset_token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.password = get_password_hash(new_password)  # Replace with hashed password
    return {"message": "Password has been reset successfully"}
