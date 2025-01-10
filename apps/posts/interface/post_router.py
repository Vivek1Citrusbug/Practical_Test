from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter
from sqlmodel import Session, select
from typing import List
from database import engine, SessionDep
from apps.posts.domain.models import Posts
from apps.posts.dependency import upload_to_minio
# from apps.user.application.service import 
router = APIRouter()


@router.post("/posts/")
def create_post(
    session: SessionDep,
    title: str,
    content: str,
    file: UploadFile | None = None,
):
    file_url = None
    if file:
        file_bytes = file.file.read()
        file_url = upload_to_minio(file_bytes, file.filename)
    post = Posts(title=title, content=content, file_url=file_url)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/posts/", response_model=List[Posts])
def list_posts(
    session: SessionDep,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
):
    query = select(Posts).offset(skip).limit(limit)
    if search:
        query = query.where(Posts.title.contains(search))
    return session.exec(query).all()


@router.get("/posts/{post_id}")
def get_post(post_id: int, session: SessionDep):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/posts/{post_id}")
def update_post(post_id: int, title: str, content: str, session: SessionDep):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.content = content
    session.commit()
    return post


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, session: SessionDep):
    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"detail": "Post deleted"}
