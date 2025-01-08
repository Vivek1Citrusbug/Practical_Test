from apps.user.application.schemas import UserBaseModel
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone

#############################
##### Database model ########
#############################


class Users(UserBaseModel, table=True):
    email: str = Field(default=None, primary_key=True)
    password: str
    password_reset_token: str = Field(default="")
    is_verified:bool = Field(default=False)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)                                            # default is active


class Profile(SQLModel, table=True):
    email: str = Field(default=None, primary_key=True)
    bio: str = Field(default=None)
    profile_picture: str = Field(default=None)
    account_type: bool = Field(default=True)                                         # default is private(1)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)                                            # default is active
