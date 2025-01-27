from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr, field_validator


#############################
##### PYDANTIC schemas ######
#############################


class UserBaseModel(SQLModel):
    username: str = Field(unique=True, nullable=False)
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


class UserCreateModel(SQLModel):
    username: str = Field(
        max_length=20,
        min_length=5,
    )
    name: str = Field(
        max_length=20,
        min_length=5,
    )
    first_name: str = Field(
        max_length=20,
        min_length=5,
    )
    last_name: str = Field(
        max_length=20,
        min_length=5,
    )
    email: EmailStr
    password: str = Field(
        max_length=20,
        min_length=8,
    )

    @field_validator("username")
    def validate_username(cls, value):
        if not value.isalnum():
            raise ValueError("Username can only contain alphanumeric characters.")
        return value

    @field_validator("name")
    def validate_name(cls, value):
        if not all(c.isalpha() or c.isspace() for c in value):
            raise ValueError("Name can only contain letters and spaces.")
        return value

    @field_validator("first_name", "last_name")
    def validate_name_fields(cls, value, info):
        if not value.isalpha():
            raise ValueError(
                f"{info.field_name.replace('_', ' ').title()} can only contain letters."
            )
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit.")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c in "@#$%^&+=" for c in value):
            raise ValueError(
                "Password must contain at least one special character (@#$%^&+=)."
            )
        return value


class UserProfileCreate(SQLModel):
    bio: str | None = Field(default=None, max_length=30)
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
