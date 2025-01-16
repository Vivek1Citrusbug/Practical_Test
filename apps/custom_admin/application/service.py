from apps.custom_admin.domain.service import delete_post_instance
from database import SessionDep
from apps.user.domain.models import Users

# def get_reported_post_application(session:SessionDep,current_user:Users):
#     """
#     Application layer service for listing reported posts
#     """
    
#     return get_reported_post_instance(session,current_user)

def delete_post_application(post_id:int,session:SessionDep,current_user:Users):
    """
    Application layer service for deleting posts
    """

    return delete_post_instance(post_id,session,current_user)