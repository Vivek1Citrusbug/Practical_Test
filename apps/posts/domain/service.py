import random
from typing import Optional
import uuid
from sqlmodel import select
from datetime import datetime, timezone, UTC
from apps.posts.domain.models import Posts, Likes, Comments, ReportedPosts
from database import SessionDep
from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, APIRouter, status
from apps.user.domain.service import get_current_user
from apps.user.domain.models import Users, Connections, Profile
from apps.posts.dependency import upload_to_minio
from apps.user.dependency import remove_object_from_minio
from config import MINIO_POST_FILE_BUCKET


def get_followers(session: SessionDep, current_user: Users):

    query = select(Connections.following).where(
        Connections.follower == current_user.username, Connections.status == 1
    )

    followings = [conn for conn in session.exec(query).all()]

    query = select(Profile.username).where(Profile.is_private_account == 0)
    public_accounts = [profile for profile in session.exec(query).all()]

    valid_usernames = list(set(followings + public_accounts))

    return valid_usernames


def create_post_instance(
    session: SessionDep,
    title: str,
    content: str,
    current_user: Users,
    file: Optional[UploadFile],
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
    username: str = None,
):
    """
    Domain layer service for listing posts
    """

    followings = get_followers(session, current_user)
    followings.append(current_user.username)

    query = select(Posts).order_by(Posts.created_at.desc())

    if username:
        user_exists = session.exec(
            select(Users).where(Users.username == username)
        ).first()
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        query = query.where(Posts.post_by == username)
    else:
        if not current_user.is_verified:
            query = query.where(Posts.post_by.in_(followings))

    query = query.offset(skip).limit(limit)

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
    random_posts: list[Posts] = random.sample(posts, min(5, len(posts)))
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
    post.modified_at = datetime.now(timezone.utc)
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

    remove_post_cloud_data(post)
    return {"detail": "Post deleted"}


def remove_post_cloud_data(post: Posts):
    """
    Service to remove post objects from minio storage
    """

    try:
        object_list = post.file_url
        object_list = object_list.split("/")
        results = []
        results.append(object_list[-1])
        remove_object_from_minio(MINIO_POST_FILE_BUCKET, results)
    except Exception as e:
        print(f"Error removing object: {str(e)}")


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
            detail="You are not permitted to report your own posts.",
        )

    if current_user.is_verified:
        reporting_post = ReportedPosts(
            post=post.id, post_by=post.post_by, reported_by=current_user.username
        )
    else:

        followings = get_followers(session, current_user)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You must follow the post author to report post.",
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

    query = select(Posts).where(Posts.id == post_id)
    post: Posts = session.exec(query).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.is_verified:
        comment = Comments(
            post=post_id, content=content, comment_by=current_user.username
        )
    else:
        followings = get_followers(session, current_user)
        followings.append(current_user.username)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=403,
                detail="You must follow the post author to create comment.",
            )

        comment = Comments(
            post=post_id, content=content, comment_by=current_user.username
        )

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
    query = select(Posts).where(Posts.id == post_id)
    post: Posts = session.exec(query).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.is_verified:
        query = select(Comments).where(Comments.post == post_id)
        comments = session.exec(query).all()
    else:
        followings = get_followers(session, current_user)
        followings.append(current_user.username)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=403,
                detail="You must follow the post author to list comments.",
            )

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
    post = session.exec(select(Posts).where(Posts.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.is_verified:
        query = select(Comments).where(
            Comments.post == post_id,
            Comments.id == comment_id,
            Comments.comment_by == current_user.username,
        )
    else:
        followings = get_followers(session, current_user)
        followings.append(current_user.username)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=404,
                detail="You must follow the post author to update comment.",
            )

        query = select(Comments).where(
            Comments.post == post_id,
            Comments.id == comment_id,
            Comments.comment_by == current_user.username,
        )

    comment = session.exec(query).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.content = content if content else comment.content
    comment.modified_at = datetime.now(UTC)

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

    query = select(Posts).where(Posts.id == post_id)
    post: Posts = session.exec(query).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not current_user.is_verified:
        followings = get_followers(session, current_user)
        followings.append(current_user.username)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=404,
                detail="You must follow the post author to delete comment.",
            )

    query = select(Comments).where(
        Comments.post == post_id,
        Comments.id == comment_id,
    )

    comment = session.exec(query).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

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

    query = select(Posts).where(Posts.id == post_id)
    post: Posts = session.exec(query).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not current_user.is_verified:
        followings = get_followers(session, current_user)
        followings.append(current_user.username)

        if post.post_by not in followings:
            raise HTTPException(
                status_code=404,
                detail="You must follow the post author to like this post.",
            )

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
