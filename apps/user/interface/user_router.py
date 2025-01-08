import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, select
from apps.user.domain.models import Users
from apps.user.application.schemas import Token
from fastapi import status
from datetime import datetime, timedelta, timezone
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from apps.user.application.schemas import (
    UserBaseModel,
    Token,
    TokenData,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine,SessionDep
from jwt.exceptions import InvalidTokenError


router = APIRouter()