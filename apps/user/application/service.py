from database import Session
from apps.user.application.schemas import UserCreateModel
from apps.user.domain.models import Users
from apps.user.domain.service import (
    register_user_instance,
    github_callback_instance,
    password_reset_instance,
    password_reset_confirm_instance
)
from database import SessionDep


async def register_user(user_data: UserCreateModel, session: Session):
    """
    Application layer service for registering new user
    """

    return await register_user_instance(user_data, session)


async def github_callback_application(code: str, session: SessionDep):
    """
    Application layer service for github callback
    """

    return await github_callback_instance(code, session)


async def password_reset_application(session: SessionDep, current_user: Users):
    """
    Application layer service generating reset password token
    """

    return await password_reset_instance(session, current_user)


async def password_reset_confirm_application(new_password:str,session: SessionDep, current_user: Users):
    """
    Application layer service generating reset password token
    """

    return await password_reset_confirm_instance(new_password,session, current_user)

