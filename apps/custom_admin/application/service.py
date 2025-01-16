from apps.custom_admin.domain.service import get_reported_post_instance
from database import SessionDep
from apps.user.domain.models import Users

def get_reported_post_application(session:SessionDep,current_user:Users):
    return get_reported_post_instance(session,current_user)