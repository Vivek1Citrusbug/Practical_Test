from fastapi import APIRouter,Depends
from apps.posts.domain.models import ReportedPosts
from apps.user.domain.models import Users
from database import SessionDep
from apps.user.domain.service import get_current_user
from apps.custom_admin.application.service import delete_post_application,get_reported_post_application

router = APIRouter()

@router.get("/reported_posts/")
def get_reported_posts(session:SessionDep,current_user:Users=Depends(get_current_user)):
    return get_reported_post_application(session,current_user)

@router.delete("/post/{post_id}/delete")
def delete_post(post_id:int,session:SessionDep,current_user:Users=Depends(get_current_user)):
    return delete_post_application(post_id,session,current_user)