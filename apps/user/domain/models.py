from apps.user.application.schemas import UserBaseModel
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from apps.posts.domain.models import Posts
from pydantic import EmailStr

#############################
##### Database model ########
#############################


class Users(UserBaseModel, table=True):
    email:EmailStr = Field(default=None, primary_key=True)
    password: str
    password_reset_token: str = Field(default="")
    is_verified: bool = Field(default=False)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    # Relationship to Profile
    profile: Optional["Profile"] = Relationship(back_populates="user")


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: str = Field(default=None)
    profile_picture: str = Field(default=None)
    is_private_account: bool = Field(default=True)  # Default is private (True)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    # Foreign key to the Users model
    username: str = Field(foreign_key="users.username", ondelete="CASCADE")

    # Relationship to Users
    user: Optional["Users"] = Relationship(back_populates="profile")


class Connections(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower: str = Field(foreign_key="users.username", ondelete="CASCADE")
    following: str = Field(foreign_key="users.username", ondelete="CASCADE")
    status: int  # status: 0 - rejected, 1 - accepted, 2 - pending
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True) 


# class Subscription(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     subscription_type: bool | None = Field(default=None)
#     expiration_at: str | None = Field(default=None)
#     created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
#     modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
#     is_active: bool = Field(default=True)


# class Transactions(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     transaction_id: str
#     username: str
#     transaction_status: str
