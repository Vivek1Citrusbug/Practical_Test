from typing import Optional
from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str
    content: str = Field(min_length=20)
