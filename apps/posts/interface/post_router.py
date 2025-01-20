from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter, status
from sqlmodel import Session, select
from typing import List
from database import engine, SessionDep
from apps.posts.domain.models import Posts, ReportedPosts, Comments, Likes
from apps.user.domain.service import get_current_user
from apps.user.domain.models import Users
from apps.posts.application.schemas import (
    PostPublicModel,
    ReportPublicModel,
    CommentPublicModel,
    CommentUpdateModel,
)
from apps.posts.application.service import (
    create_post_application,
    list_posts_application,
    update_post_application,
    delete_post_application,
    report_post_application,
    create_comment_application,
    list_comments_application,
    update_comment_application,
    delete_comment_application,
    create_like_application,
    list_recommended_posts_application
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
    return create_post_application(session, title, content, file, current_user)


@router.get("/", response_model=List[PostPublicModel])
def list_posts(
    session: SessionDep,
    skip: int = 0,
    limit: int = 10,
    post_id: int = None,
    username: str = None,
    current_user: Users = Depends(get_current_user),
):
    return list_posts_application(session, skip, limit, post_id, username, current_user)


@router.get("/recommended_posts/", response_model=List[PostPublicModel])
def list_posts(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return list_recommended_posts_application(session, current_user)


@router.put("/{post_id}/", response_model=PostPublicModel)
def update_post(
    post_id: int,
    session: SessionDep,
    title: str | None = None,
    content: str | None = None,
    file: UploadFile | None = None,
    current_user: Users = Depends(get_current_user),
):
    return update_post_application(post_id, session, title, content, file, current_user)


@router.delete("/{post_id}/")
def delete_post(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return delete_post_application(post_id, session, current_user)


@router.post("/{post_id}/report/", response_model=ReportPublicModel)
def report_post(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return report_post_application(post_id, session, current_user)


@router.post("{post_id}/comments/create/", response_model=CommentPublicModel)
def post_comment(
    post_id: int,
    content,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return create_comment_application(post_id, content, session, current_user)


@router.get("{post_id}/comments", response_model=list[CommentPublicModel])
def get_comment(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return list_comments_application(post_id, session, current_user)


@router.put("{post_id}/comments/{comment_id}/", response_model=CommentUpdateModel)
def comment_update(
    post_id,
    content,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return update_comment_application(
        post_id, content, comment_id, session, current_user
    )


@router.delete(
    "{post_id}/comments/{comment_id}/delete/", status_code=status.HTTP_200_OK
)
def delete_comment(
    post_id,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    return delete_comment_application(post_id, comment_id, session, current_user)


@router.post("{post_id}/like")
def like_post(
    post_id, session: SessionDep, current_user: Users = Depends(get_current_user)
):
    return create_like_application(post_id, session, current_user)
