from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter, status
from sqlmodel import Session, select
from typing import List
from database import engine, SessionDep
from apps.posts.domain.models import Posts, ReportedPosts, Comments
from apps.posts.dependency import upload_to_minio
from apps.user.domain.service import get_current_user
from apps.user.domain.models import Users
from apps.posts.application.schemas import (
    PostPublicModel,
    ReportPublicModel,
    CommentPublicModel,
    CommentUpdateModel,
)

router = APIRouter()


@router.post("/", response_model=PostPublicModel)
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


@router.get("/", response_model=List[PostPublicModel])
def list_posts(
    session: SessionDep,
    skip: int = 0,
    limit: int = 10,
    post_id: int = None,
    username: str = None,
    current_user: Users = Depends(get_current_user),
):
    query = select(Posts).offset(skip).limit(limit)
    if username:
        query = query.where(Posts.post_by.contains(username))

    if post_id:
        query = query.where(Posts.id.contains(post_id))
    return session.exec(query).all()


@router.put("/{post_id}/", response_model=PostPublicModel)
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


@router.delete("/{post_id}/")
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


@router.post("/{post_id}/report/", response_model=ReportPublicModel)
def report_post(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    query = select(Posts).where(Posts.id == post_id)
    post: Posts = session.exec(query).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.post_by == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this task.",
        )

    reporting_post = ReportedPosts(
        post=post.id, post_by=post.post_by, reported_by=current_user.username
    )
    session.add(reporting_post)
    session.commit()
    session.refresh(reporting_post)
    return reporting_post


@router.post("{post_id}/comments/create/", response_model=CommentPublicModel)
def post_comment(
    post_id: int,
    content,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    comment = Comments(post=post_id, content=content, comment_by=current_user.username)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.get("{post_id}/comments", response_model=list[CommentPublicModel])
def post_comment(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    query = select(Comments).where(Comments.post == post_id)
    comments = session.exec(query).all()

    if not comments:
        return []  # Return an empty list if no comments exist

    return comments


@router.put("{post_id}/comments/{comment_id}/", response_model=CommentUpdateModel)
def comment_update(
    post_id,
    content,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    query = select(Comments).where(
        Comments.post == post_id,
        Comments.id == comment_id,
        Comments.comment_by == current_user.username,
    )
    comment = session.exec(query).first()
    comment.content = content if content else comment.content
    comment.modified_at = datetime.now(timezone.utc)
    session.commit()
    return comment


@router.delete(
    "{post_id}/comments/{comment_id}/delete/", status_code=status.HTTP_200_OK
)
def delete_comment(
    post_id,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    query = select(Comments).where(
        Comments.post == post_id,
        Comments.id == comment_id,
    )
    comment = session.exec(query).first()
    if comment.comment_by != current_user.username and not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this task.",
        )
    session.delete(comment)
    session.commit()
    return {"message": "Comment deleted successfully"}
