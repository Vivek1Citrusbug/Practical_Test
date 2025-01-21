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
    email: EmailStr
    name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)


# class UserCreateModel(SQLModel):
#     username: str = Field(max_length=20,min_length=5,regex=r"^[a-zA-Z0-9_]+$")
#     name: str = Field(max_length=20,regex=r"^[a-zA-Z\s]+$")
#     first_name: str = Field(max_length=20,regex=r"^[a-zA-Z]+$")
#     last_name: str = Field(max_length=20, regex=r"^[a-zA-Z]+$")
#     email: EmailStr
#     password: str = Field(max_length=20,min_length=8,regex=r"^\(?=.*[A-Za-z])\(?=.*\d).{8,}$")


class UserCreateModel(SQLModel):
    username: str = Field(
        max_length=20, 
        min_length=5, 
        regex=r"^[a-zA-Z0-9_]+$"  # Allows letters, numbers, and underscores
    )
    name: str = Field(
        max_length=20, 
        regex=r"^[a-zA-Z\s]+$"  # Allows letters and spaces
    )
    first_name: str = Field(
        max_length=20, 
        regex=r"^[a-zA-Z]+$"  # Allows only letters
    )
    last_name: str = Field(
        max_length=20, 
        regex=r"^[a-zA-Z]+$"  # Allows only letters
    )
    email: EmailStr  # Ensures a valid email format
    password: str = Field(
        max_length=20, 
        min_length=8, 
        regex=r"^(?=.*[A-Za-z])(?=.*\d).{8,}$"  # At least 1 letter, 1 digit, and 8+ chars
    )

class UserProfileCreate(SQLModel):
    bio: str | None = Field(default=None,max_length=30)
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
    email: EmailStr | None = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


