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
)
from apps.user.dependency import ConnectionResponse
from datetime import datetime, timedelta, timezone
from config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    GITHUB_CLIENT_ID,
    STRIPE_API_KEY,
    STRIPE_SUCCESS_URL,
    STRIPE_FAILURE_URL,
    STRIPE_ENDPOINT_SECRET_KEY,
)
from apps.user.application.schemas import Token, UserProfileCreate, UserProfilePublic
from apps.user.domain.models import Connections,Transaction,Subscription
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
)
from fastapi import status, File

router = APIRouter()

stripe.api_key = STRIPE_API_KEY


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


@router.post("/password-reset/{username}/", tags=["Users"])
async def password_reset_request(
    session: SessionDep,
    # current_user: Users = Depends(get_current_user),
    username:str
):
    return await password_reset_application(session, username)


@router.post("/password-reset/confirm/{username}/", tags=["Users"])
async def password_reset_confirm(
    new_password: str,
    session: SessionDep,
    username:str,
    # current_user: Users = Depends(get_current_user),
):

    return await password_reset_confirm_application(new_password, session, username)


@router.post("/profiles/", response_model=UserProfilePublic, tags=["Profile"])
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


@router.get("/profiles/{username}/", response_model=UserProfilePublic, tags=["Profile"])
async def get_profile(username: str, session: SessionDep):
    return await user_profile_get_application(username, session)


@router.put("/profiles/{username}/", response_model=UserProfilePublic, tags=["Profile"])
async def update_profile(
    bio: str | None,
    is_private_account: bool | None,
    session: SessionDep,
    file: Optional[list[UploadFile]] = File(None),
    current_user: Users = Depends(get_current_user),
):
    return await user_profile_update_application(
        bio, is_private_account, session, file, current_user
    )


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
    return await create_connection_application(username, session, current_user)


@router.post("/connection/unfollow/", tags=["Connections"])
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
async def checkout(amount: int, session: SessionDep,current_user: Users = Depends(get_current_user)):
    if amount != 500:
        raise HTTPException(status_code=400, detail="Amount must be $5")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Subscription"},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=STRIPE_SUCCESS_URL,
            cancel_url=STRIPE_FAILURE_URL,
        )
        print(session)
        
        # # Simulate payment process and create a pending transaction
        # transaction = Transaction(
        #     username=current_user.username,
        #     subscription_id=user.subscription.id,  # Reference to the subscription
        #     amount=current_user.subscription.monthly_fee,
        #     payment_status="pending",
        #     payment_method="card"
        # )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating checkout session: {str(e)}"
        )


# @router.post("/webhook")
# async def stripe_webhook(
#     request: Request,
#     db_session: SessionDep,
#     current_user: Users = Depends(get_current_user),
# ):
#     payload = await request.body()
#     sig_header = request.headers.get("Stripe-Signature")
#     endpoint_secret = STRIPE_ENDPOINT_SECRET_KEY

#     try:
#         event = stripe.Webhook.construct_event(
#             payload=payload, sig_header=sig_header, secret=endpoint_secret
#         )
#     except stripe.error.SignatureVerificationError as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

#     if event["type"] in [
#         "payment_intent.succeeded",
#         "charge.updated",
#         "charge.succeeded",
#     ]:
#         payment_obj = event["data"]["object"]
#         customer_email = payment_obj.get("billing_details", {}).get("email")
#         if not customer_email:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email not found in payment details",
#             )

#         statement = select(Users).where(Users.email == customer_email)
#         user = db_session.exec(statement).first()

#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#             )

#         user.is_staff = True
#         user.is_superuser = True

#         db_session.add(user)
#         db_session.commit()

#         # # schedule task for the eta
#         # revert_user_role.apply_async(args=[user.email], eta=user.expiration_time)

#     else:
#         print(f"Unhandled event type: {event['type']}")
#     return {"status": "success"}
