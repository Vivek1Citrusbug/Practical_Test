import httpx
import stripe
from fastapi.responses import RedirectResponse
import jwt
from typing import Annotated, Optional
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    UploadFile,
    requests,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, select
from apps.user.domain.models import Users, Profile
from apps.user.application.schemas import (
    Token,
    UserCreateModel,
    UserPublicModel,
    BaseResponse
)
from apps.user.dependency import ConnectionResponse
from datetime import datetime, timedelta, timezone
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
    STRIPE_SECRET_API_KEY,
    STRIPE_SUCCESS_URL,
    STRIPE_FAILURE_URL,
    STRIPE_ENDPOINT_SECRET_KEY,
)
from apps.user.application.schemas import Token, UserProfileCreate, UserProfilePublic
from apps.user.domain.models import Connections, Transaction, Subscription
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
    remove_follower_application,
    create_checkout_session_application,
    stripe_webhook_application,
)
from fastapi import status, File

router = APIRouter()

stripe.api_key = STRIPE_SECRET_API_KEY


@router.post("/register", response_model=BaseResponse[UserPublicModel], tags=["Users"])
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
    token_data = Token(access_token=access_token, token_type="bearer")
    return token_data


@router.get("/github/login", tags=["Users"])
def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=read:user,user:email"
    )
    result = {"auth_url": github_auth_url}
    return BaseResponse(success=True,data=result,message="Please authorize using provided url!")  


@router.get("/github/callback", tags=["Users"])
async def github_callback(code: str, session: SessionDep):
    return await github_callback_application(code, session)


@router.post("/password-reset/{username}/", tags=["Users"])
async def password_reset_request(
    session: SessionDep,
    username: str,
):
    return await password_reset_application(session, username)


@router.post("/password-reset/confirm/{username}/", tags=["Users"])
async def password_reset_confirm(
    new_password: str,
    session: SessionDep,
    username: str,
):

    return await password_reset_confirm_application(new_password, session, username)


@router.post("/profiles/", response_model=BaseResponse[UserProfilePublic], tags=["Profile"])
async def create_profile(
    session: SessionDep,
    file: Optional[list[UploadFile]] = File(None),
    bio: str = Form(...),
    is_private_account: bool = Form(...),
    current_user: Users = Depends(get_current_user),
):

    return await user_profile_create_application(
        bio, is_private_account, session, current_user, file
    )


@router.get("/profiles/{username}/", response_model= BaseResponse[UserProfilePublic], tags=["Profile"])
async def get_profile(username: str, session: SessionDep):
    return await user_profile_get_application(username, session)


@router.put("/profiles/{username}/", response_model=BaseResponse[UserProfilePublic], tags=["Profile"])
async def update_profile(
    session: SessionDep,
    bio: str | None = Form(...),
    is_private_account: bool | None = Form(...),
    file: Optional[list[UploadFile]] | None = File(None),
    current_user: Users = Depends(get_current_user),
):
    return await user_profile_update_application(
        bio, is_private_account, session, current_user, file
    )


@router.delete("/profiles/{username}", tags=["Profile"],response_model=BaseResponse[UserProfilePublic])
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
    return await create_connection_application(username, session, current_user)


@router.put("/connection/unfollow/", tags=["Connections"])
async def unfollow_user(
    username: str,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await unfollow_user_application(username, session, current_user)


@router.get("/connection/requests/", tags=["Connections"])
async def follow_requests(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_connection_requests_application(session, current_user)


@router.post("/connection/request/status", tags=["Connections"])
async def handle_requests(
    username: str,
    response: ConnectionResponse,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await handle_connection_requests_application(
        username, response, session, current_user
    )


@router.get("/followers/", tags=["Connections"])
async def get_followers(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_followers_application(session, current_user)


@router.get("/following/", tags=["Connections"])
async def get_following(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return await get_following_application(session, current_user)


@router.delete("/connection/remove_follower/", tags=["Connections"])
async def remove_follower(
    username: str, session: SessionDep, current_user: Users = Depends(get_current_user)
):
    return await remove_follower_application(
        username=username, session=session, current_user=current_user
    )


@router.post("/create-checkout-session")
async def checkout(amount: int, session: SessionDep):
    return await create_checkout_session_application(amount, session)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db_session: SessionDep,
):
    return await stripe_webhook_application(request, db_session)
