from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter
from sqlmodel import Session, select
from typing import List
from database import engine, SessionDep
from apps.posts.domain.models import Posts
from apps.posts.dependency import upload_to_minio
from apps.user.domain.service import get_current_user
from apps.user.domain.models import Users
from apps.posts.application.schemas import PostPublicModel

router = APIRouter()


@router.post("/posts/", response_model=PostPublicModel)
def create_post(
    session: SessionDep,
    title: str,
    content: str,
    file: UploadFile | None = None,
    current_user: Users = Depends(get_current_user),
):
    file_url = None
    if file:
        file_bytes = file.file.read()
        file_url = upload_to_minio(file_bytes, file.filename)
    post = Posts(
        title=title, content=content, file_url=file_url, post_by=current_user.username
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/posts/", response_model=List[PostPublicModel])
def list_posts(
    session: SessionDep,
    skip: int = 0,
    limit: int = 10,
    username: str = None,
    current_user: Users = Depends(get_current_user),
):
    query = select(Posts).offset(skip).limit(limit)
    if username:
        query = query.where(Posts.post_by.contains(username))
    return session.exec(query).all()


@router.put("/posts/{post_id}", response_model=PostPublicModel)
def update_post(
    post_id: int,
    session: SessionDep,
    title: str | None = None,
    content: str | None = None,
    file: UploadFile | None = None,
    current_user: Users = Depends(get_current_user),
):

    post = session.get(Posts, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.post_by != current_user.username:
        raise HTTPException(
            status_code=403, detail="You are not the owner of this post"
        )

    file_url = None
    if file:
        file_bytes = file.file.read()
        file_url = upload_to_minio(file_bytes, file.filename)

    post.title = title if title else post.title
    post.content = content if content else post.content
    post.file_url = file_url if file_url else post.file_url
    session.commit()

    return post


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.post_by != current_user.username and not (
        current_user.is_staff or current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403, detail="You are not authorized to perform this task."
        )
    session.delete(post)
    session.commit()
    return {"detail": "Post deleted"}
