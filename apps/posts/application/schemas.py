from typing import Optional
from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str
    content: str = Field(min_length=20)

class PostPublicModel(SQLModel):
    id:int
    post_by: str
    title: str
    content:str 
    file_url: Optional[str] = Field(default=None)
    created_at: str
