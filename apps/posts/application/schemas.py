from typing import Optional
from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str
    content: str = Field(min_length=20)


class PostPublicModel(SQLModel):
    id: int
    post_by: str
    title: str
    content: str
    file_url: Optional[str] = Field(default=None)
    created_at: str


class ReportPublicModel(SQLModel):
    post: int
    post_by: str
    reported_by: str
    created_at: str


class CommentPublicModel(SQLModel):
    id: int
    comment_by: str
    content: str
    created_at: str


class CommentUpdateModel(SQLModel):
    comment_by: str
    content: str
    modified_at: str
