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
)
from apps.user.application.schemas import (
    UserBaseModel,
    Token,
    TokenData,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine, SessionDep
from jwt.exceptions import InvalidTokenError
from apps.user.dependency import get_current_active_user, get_current_user
from apps.user.domain.service import (
    create_access_token,
    get_password_hash,
    verify_password,
    authenticate_user,
)
from database import Session
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient

router = APIRouter()


# User registration endpoint
@router.post("/register", response_model=UserPublicModel)
async def register(user: UserCreateModel, session: SessionDep):
    """
    Function to create user based on the allowed roles
    """

    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    UserDatabase = Users.model_validate(user_data)
    session.add(UserDatabase)
    session.commit()
    session.refresh(UserDatabase)
    return UserDatabase


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


@router.get("/auth/github/callback")
async def github_callback(code: str):
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

    jwt_token = create_access_token(
        {"username": user_data["login"], "sub": user_data["id"]}
    )
    return {"jwt_token": jwt_token, "user": user_data}

@router.get("/users/me", response_model=UserPublicModel)
def read_logged_in_user(current_user: UserPublicModel = Depends(get_current_user)):
    return current_user
