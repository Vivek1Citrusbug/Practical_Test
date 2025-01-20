from apps.posts.application.schemas import PostBase
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import Optional

#############################
##### Database model ########
#############################


class Posts(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_by: str = Field(foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE")
    file_url: Optional[str] = Field(default=None)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    
    # Relationship with ReportedPosts
    reported_posts: list["ReportedPosts"] = Relationship(back_populates="post_model")

class ReportedPosts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post: int = Field(foreign_key="posts.id", index=True, nullable=False,ondelete="CASCADE")
    post_by: str = Field(foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE")
    reported_by: str = Field(foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

    # Relationship with Posts
    post_model: Optional[Posts] = Relationship(back_populates="reported_posts")


class Likes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post: int = Field(foreign_key="posts.id", index=True, nullable=False)
    liked_by: str = Field(foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)


class Comments(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post: int = Field(foreign_key="posts.id", index=True, nullable=False)
    content: str = Field(max_length=100)
    comment_by: str = Field(foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
