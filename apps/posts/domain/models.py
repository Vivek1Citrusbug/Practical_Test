from apps.posts.application.schemas import PostBase
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
from typing import Optional

#############################
##### Database model ########
#############################


class Posts(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_by: str = Field(foreign_key="users.username", index=True, nullable=False)
    file_url: Optional[str] = Field(default=None)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
