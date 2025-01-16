from sqlmodel import select
from apps.posts.domain.models import ReportedPosts
from database import SessionDep
from apps.user.domain.models import Users
from fastapi import HTTPException, status

def get_reported_post_instance(session:SessionDep,current_user:Users):
    """
    Domain layer service for listing reported post of the users.
    """

    if current_user.is_staff or current_user.is_superuser:
        query = select(ReportedPosts.post).distinct()
        reported_posts = session.exec(query).all()
        return reported_posts
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized to perform this task")