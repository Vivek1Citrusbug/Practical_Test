from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr


#############################
##### PYDANTIC schemas ######
#############################


class UserBaseModel(SQLModel):
    username: str = Field(unique=True,nullable=False)
    name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)


class UserPublicModel(SQLModel):
    username: str
    email: str
    name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)


class UserCreateModel(SQLModel):
    username: str
    name: str
    first_name: str
    last_name: str
    email: str
    password: str


class UserProfileCreate(SQLModel):
    bio: str | None = Field(default=None)
    is_private_account: bool


class UserProfilePublic(SQLModel):
    bio: str | None = Field(default=None)
    profile_picture: str | None = Field(default=None)
    is_private_account: bool
    created_at: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str
    email: str | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr
