from sqlmodel import select
from apps.posts.domain.models import ReportedPosts
from database import SessionDep
from apps.user.domain.models import Users
from apps.posts.domain.models import Posts
from fastapi import HTTPException, status
from apps.custom_admin.dependency import send_post_removal_email


def get_reported_post_instance(session: SessionDep, current_user: Users):
    """
    Domain layer service for listing reported post of the users.
    """

    if current_user.is_staff or current_user.is_superuser:
        reported_posts = session.exec(select(ReportedPosts).distinct()).all()
        result = {}
        for reported_post in reported_posts:
            post_id = reported_post.post
            reported_by = reported_post.reported_by
            if post_id not in result:
                result[post_id] = []
            result[post_id].append(reported_by)
        # returning dictionary having post id as key and list of user who reported that post as value
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this task",
        )


def delete_post_instance(post_id: int, session: SessionDep, current_user: Users):

    if current_user.is_staff or current_user.is_superuser:
        deleting_post = session.exec(select(Posts).where(Posts.id == post_id)).first()

        if not deleting_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )

        session.delete(deleting_post)
        session.commit()

        target_user = session.exec(
            select(Users).where(Users.username == deleting_post.post_by)
        ).first()

        send_post_removal_email(
            target_user.email,
            target_user.username,
            deleting_post.title,
            removal_reason="Your post has been removed as it does not comply with our company's content policy.",
        )   
        return {"detail": "Post deleted successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this task.",
        )
