import httpx
from fastapi.responses import RedirectResponse
import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, requests
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, select
from apps.user.domain.models import Users, Profile
from apps.user.application.schemas import (
    Token,
    UserCreateModel,
    UserPublicModel,
)

from datetime import datetime, timedelta, timezone
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
)
from apps.user.application.schemas import Token, UserProfileCreate, UserProfilePublic
from apps.user.domain.models import Connections
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, SessionDep
from apps.user.domain.service import (
    create_access_token,
    authenticate_user,
    get_current_user,
)
from database import Session
from apps.user.application.service import (
    register_user,
    github_callback_application,
    password_reset_application,
    password_reset_confirm_application,
    user_profile_delete_application,
    user_profile_update_application,
    user_profile_create_application,
    user_profile_get_application,
    create_connection_application,
    get_connection_requests_application,
    handle_connection_requests_application,
    get_followers_application,
    get_following_application,
    unfollow_user_application,
)
from fastapi import status

router = APIRouter()

@router.post("/register", response_model=UserPublicModel, tags=["Users"])
async def register(user: UserCreateModel, session: SessionDep):
    """
    Function to create user based on the allowed roles
    """
    return await register_user(user, session)

@router.post("/token", status_code=status.HTTP_201_CREATED, tags=["Users"])
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


@router.get("/github/login", tags=["Users"])
def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=read:user,user:email"
    )
    return {"auth_url": github_auth_url}


@router.get("/github/callback", tags=["Users"])
async def github_callback(code: str, session: SessionDep):
    return await github_callback_application(code, session)


@router.post("/password-reset/", tags=["Users"])
async def password_reset_request(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await password_reset_application(session, current_user)


@router.post("/password-reset/confirm/", tags=["Users"])
async def password_reset_confirm(
    new_password: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):

    return await password_reset_confirm_application(new_password, session, current_user)


@router.post("/profiles/", response_model=UserProfilePublic, tags=["Profile"])
async def create_profile(
    session: SessionDep,
    bio: str = Form(...),
    is_private_account: bool = Form(...),
    current_user: Users = Depends(get_current_user),
    file: UploadFile | None = None,
):

    return await user_profile_create_application(bio,is_private_account, session, current_user,file)


@router.get("/profiles/{username}", response_model=UserProfilePublic, tags=["Profile"])
async def get_profile(username: str, session: SessionDep):
    return await user_profile_get_application(username, session)


@router.put("/profiles/{username}", response_model=UserProfilePublic, tags=["Profile"])
async def update_profile(
    profile_data: UserProfileCreate,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await user_profile_update_application(profile_data, session, current_user)


@router.delete("/profiles/{username}", tags=["Profile"])
async def delete_profile(
    username: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):

    return await user_profile_delete_application(username, session, current_user)


@router.post("/connection/{username}/", tags=["Connections"])
async def create_follow_request(
    username: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await create_connection_application(username,session,current_user)

@router.post("/connection/",tags=["Connections"])
async def unfollow_user(
    username:str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),):
    return await unfollow_user_application(username,session,current_user)

@router.get("/connection/requests/",tags=["Connections"])
async def follow_requests(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_connection_requests_application(session,current_user)

@router.post("/connection/request/status",tags=["Connections"])
async def handle_requests(
    username:str,
    response:str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await handle_connection_requests_application(username,response,session,current_user)

@router.get("/followers/",tags=["Connections"])
async def get_followers(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_followers_application(session,current_user)


@router.get("/following/",tags=["Connections"])
async def get_following(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_following_application(session,current_user)