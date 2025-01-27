from apps.user.application.schemas import UserBaseModel
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, List
from apps.posts.domain.models import Posts
from pydantic import EmailStr

#############################
##### Database model ########
#############################


class Users(UserBaseModel, table=True):
    email: EmailStr = Field(default=None, primary_key=True)
    password: str
    password_reset_token: str = Field(default="")
    is_verified: bool = Field(default=False)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    # Relationship to Profile
    profile: Optional["Profile"] = Relationship(back_populates="user")

    subscription: Optional["Subscription"] = Relationship(back_populates="users")

    transactions: Optional["Transaction"] = Relationship(back_populates="user")


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(default="free")  # 'free' or 'paid'
    amount: int = Field(default=0)
    expire_at: Optional[str] = Field(default=None)
    username: str = Field(foreign_key="users.username", ondelete="CASCADE")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    users: Optional["Users"] = Relationship(back_populates="subscription")
    transactions: Optional["Transaction"] = Relationship(back_populates="subscription")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="users.username", ondelete="CASCADE")
    subscription_id: int = Field(foreign_key="subscription.id", ondelete="CASCADE",nullable=True)
    payment_status: str  # 'paid', 'failed', 'pending' 
    payment_intent_id:str
    user: Optional["Users"] = Relationship(back_populates="transactions")
    subscription: Optional["Subscription"] = Relationship(back_populates="transactions")


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
