from fastapi import Depends, UploadFile
from apps.posts.domain.service import (
    create_post_instance,
    list_posts_instance,
    update_post_instance,
    delete_post_instance,
    report_post_instance,
    create_comment_instance,
    list_comments_instance,
    update_comment_instance,
    delete_comment_instance,
    create_like_instance,
    list_recommended_posts_instance
)
from apps.user.domain.models import Users
from apps.user.domain.service import get_current_user
from database import SessionDep


def create_post_application(
    session: SessionDep,
    title: str,
    content: str,
    current_user: Users,
    file: UploadFile | None = None,
):
    """
    Application layer service for creating post
    """

    return create_post_instance(session, title, content,  current_user, file)


def list_posts_application(
    session: SessionDep,
    current_user: Users,
    skip: int = 0,
    limit: int = 10,
    username: str = None,
):
    """
    Application layer service for listing posts
    """

    return list_posts_instance(session,current_user, skip, limit, username)

def list_recommended_posts_application(
    session: SessionDep,
    current_user: Users,
):
    """Application layer service for listing recommended post to users"""
    return list_recommended_posts_instance(session,current_user)
    

def update_post_application(
    post_id: int,
    session: SessionDep,
    current_user: Users,
    title: str | None = None,
    content: str | None = None,
    file: UploadFile | None = None,
):
    """
    Application layer service for updating post
    """

    return update_post_instance(post_id, session, current_user, title, content, file)


def delete_post_application(
    post_id: int,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for deleting post
    """

    return delete_post_instance(post_id, session, current_user)


def report_post_application(
    post_id: int,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for reporting post
    """

    return report_post_instance(post_id, session, current_user)


def create_comment_application(
    post_id: int,
    content,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for creating comment
    """

    return create_comment_instance(post_id, content, session, current_user)


def list_comments_application(
    post_id: int,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for listing comments
    """

    return list_comments_instance(post_id, session, current_user)


def update_comment_application(
    post_id,
    content,
    comment_id,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for updating comments
    """

    return update_comment_instance(post_id, content, comment_id, session, current_user)

def delete_comment_application(
    post_id,
    comment_id,
    session: SessionDep,
    current_user: Users,
):
    """
    Application layer service for deleting comment
    """
    
    return delete_comment_instance(post_id,comment_id,session,current_user)

def create_like_application(
    post_id, 
    session: SessionDep, 
    current_user: Users,
):
    """
    Application layer service for creating like
    """

    return create_like_instance(post_id,session,current_user)