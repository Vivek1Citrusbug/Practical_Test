import httpx
from fastapi.responses import RedirectResponse
import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, requests
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, select
from apps.user.domain.models import Users, Profile
from apps.user.application.schemas import (
    Token,
    UserCreateModel,
    UserPublicModel,
)
from fastapi import status
from datetime import datetime, timedelta, timezone
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
)
from apps.user.application.schemas import Token, UserProfileCreate, UserProfilePublic
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
)

router = APIRouter()


@router.post("/register", response_model=UserPublicModel,tags=["Users"])
async def register(user: UserCreateModel, session: SessionDep):
    """
    Function to create user based on the allowed roles
    """
    return await register_user(user, session)


@router.post(
    "/token",
    status_code=status.HTTP_201_CREATED,tags=["Users"]
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


@router.get("/github/login",tags=["Users"])
def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=read:user,user:email"
    )
    return {"auth_url": github_auth_url}


@router.get("/github/callback",tags=["Users"])
async def github_callback(code: str, session: SessionDep):
    return await github_callback_application(code, session)


@router.post("/password-reset/",tags=["Users"])
async def password_reset_request(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await password_reset_application(session, current_user)


@router.post("/password-reset/confirm/",tags=["Users"])
async def password_reset_confirm(
    new_password: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):

    return await password_reset_confirm_application(new_password, session, current_user)


@router.post("/profiles/", response_model=Profile,tags=["Profile"])
def create_profile(
    profile: UserProfileCreate,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):

    if getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admins cannot have profiles")

    existing_profile = session.exec(
        select(Profile).where(Profile.username == current_user.username)
    ).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="User already has a profile")

    new_profile = Profile(
        bio=profile.bio,
        profile_picture=profile.profile_picture,
        is_private_account=profile.is_private_account,
        username=current_user.username,
    )
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    return new_profile


@router.get("/profiles/{username}", response_model=UserProfilePublic,tags=["Profile"])
def get_profile(username: str, session: SessionDep):
    profile = session.exec(select(Profile).where(Profile.username == username)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profiles/{username}", response_model=UserProfilePublic,tags=["Profile"])
def update_profile(
    profile_data: UserProfileCreate,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    profile = session.exec(
        select(Profile).where(Profile.username == current_user.username)
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.bio = profile_data.bio if profile_data.bio is not None else profile.bio
    profile.profile_picture = (
        profile_data.profile_picture
        if profile_data.profile_picture is not None
        else profile.profile_picture
    )
    profile.is_private_account = (
        profile_data.is_private_account
        if profile_data.is_private_account is not None
        else profile.is_private_account
    )
    profile.modified_at = datetime.now(timezone.utc)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.delete("/profiles/{username}",tags=["Profile"])
def delete_profile(
    username: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):

    profile = session.exec(select(Profile).where(Profile.username == username)).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if (
        current_user.username == username
        or current_user.is_staff
        or current_user.is_superuser
    ):  # only admin or one who owns the profile will be able to delete profile
        session.delete(profile)
        session.commit()
        return {"detail": "Profile deleted successfully"}
