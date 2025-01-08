import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
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
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from apps.user.application.schemas import (
    UserBaseModel,
    Token,
    TokenData,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine, SessionDep
from jwt.exceptions import InvalidTokenError
from apps.user.dependency import get_current_active_user, get_current_user
from apps.user.domain.service import create_access_token,get_password_hash
router = APIRouter()


# User registration endpoint
@router.post("/register", response_model=UserPublicModel)
async def register(user: UserCreateModel,session: SessionDep):
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























# # Login endpoint to issue JWT token
# @router.post("/login")
# async def login(user: UserCreate):
#     db_user = get_user_from_db(user.username)
#     if not db_user or not verify_password(user.password, db_user["password"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     token = create_access_token(data={"sub": user.username})
#     return {"access_token": token, "token_type": "bearer"}


# # GitHub login endpoint
# @router.post("/github-login")
# async def github_login(token: str):
#     user_data = await get_github_user(token)
#     # In real scenario, check user existence in DB, or create a new user
#     return {"message": "Logged in via GitHub", "user_data": user_data}


# # Protected route example
# @router.get("/profile")
# async def read_profile(current_user: str = Depends(get_current_user)):
#     return {"message": f"Hello {current_user}, you are authorized!"}
