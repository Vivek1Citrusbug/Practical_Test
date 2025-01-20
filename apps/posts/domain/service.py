import random
import uuid
from sqlmodel import select
from datetime import datetime, timezone
from apps.posts.domain.models import Posts, Likes, Comments, ReportedPosts
from database import SessionDep
from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter, status
from apps.user.domain.service import get_current_user
from apps.user.domain.models import Users
from apps.posts.dependency import upload_to_minio


def create_post_instance(
    session: SessionDep,
    title: str,
    content: str,
    current_user: Users,
    file: UploadFile | None = None,
):
    """
    Domain layer service for creating post
    """

    try:
        file_url = None
        if file:
            file_bytes = file.file.read()
            file_extension = (
                file.filename.split(".")[-1] if "." in file.filename else ""
            )
            file_url = upload_to_minio(
                file_bytes, str(uuid.uuid4()) + "." + file_extension
            )

        post = Posts(
            title=title,
            content=content,
            file_url=file_url,
            post_by=current_user.username,
        )

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the post: {str(e)}",
        )


def list_posts_instance(
    session: SessionDep,
    current_user: Users,
    skip: int = 0,
    limit: int = 10,
    post_id: int = None,
    username: str = None,
):
    """
    Domain layer service for listing posts
    """

    query = select(Posts).offset(skip).limit(limit)
    if username:
        query = query.where(Posts.post_by.contains(username))

    if post_id:
        query = query.where(Posts.id.contains(post_id))
    return session.exec(query).all()


def list_recommended_posts_instance(session: SessionDep, current_user: Users):
    """
    Domain layer service for listing post recommendation
    """

    query = select(Likes).filter(Likes.liked_by == current_user.username)
    liked_posts = session.exec(query).all()
    liked_post_ids = [like.post for like in liked_posts]
    print(liked_post_ids)
    query = select(Posts).filter(
        Posts.id.not_in(liked_post_ids), Posts.post_by != current_user.username
    )
    posts = session.exec(query).all()
    random_posts = random.sample(posts, min(5, len(posts)))
    return random_posts


def update_post_instance(
    post_id: int,
    session: SessionDep,
    current_user: Users,
    title: str | None = None,
    content: str | None = None,
    file: UploadFile | None = None,
):
    """
    Domain layer service for updating post
    """

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


def delete_post_instance(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for deleting post
    """

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


def report_post_instance(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for reporting post
    """

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


def create_comment_instance(
    post_id: int,
    content,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for creating comment
    """

    comment = Comments(post=post_id, content=content, comment_by=current_user.username)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


def list_comments_instance(
    post_id: int,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for listing comments
    """

    query = select(Comments).where(Comments.post == post_id)
    comments = session.exec(query).all()

    if not comments:
        return []

    return comments


def update_comment_instance(
    post_id,
    content,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for updating comment
    """

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


def delete_comment_instance(
    post_id,
    comment_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for deleting comment
    """

    query = select(Comments).where(
        Comments.post == post_id,
        Comments.id == comment_id,
    )
    comment = session.exec(query).first()
    if comment.comment_by != current_user.username and not (
        current_user.is_staff or current_user.is_superuser
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this task.",
        )
    session.delete(comment)
    session.commit()
    return {"message": "Comment deleted successfully"}


def create_like_instance(
    post_id,
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
):
    """
    Domain layer service for creating like
    """

    post = session.get(Posts, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    query = select(Likes).where(
        (Likes.post == post_id) & (Likes.liked_by == current_user.username)
    )
    existing_like = session.exec(query).first()

    if existing_like:
        session.delete(existing_like)
        session.commit()
        return {"message": "Post unliked"}
    else:
        like = Likes(post=post_id, liked_by=current_user.username)
        session.add(like)
        session.commit()
        return {"message": "Post liked"}
