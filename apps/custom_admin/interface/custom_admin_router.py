from apps.custom_admin.application.service import get_reported_post_application
from fastapi import APIRouter,Depends
from apps.posts.domain.models import ReportedPosts
from apps.user.domain.models import Users
from database import SessionDep
from apps.user.domain.service import get_current_user

router = APIRouter()

@router.get("/reported_posts/")
def get_reported_posts(session:SessionDep,current_user:Users=Depends(get_current_user)):
    return get_reported_post_application(session,current_user)