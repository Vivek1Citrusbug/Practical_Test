from database import Session
from apps.user.application.schemas import UserCreateModel, UserProfileCreate
from apps.user.domain.models import Users
from apps.user.domain.service import (
    register_user_instance,
    github_callback_instance,
    password_reset_instance,
    password_reset_confirm_instance,
    user_profile_delete_instance,
    user_profile_update_instance,
    user_profile_create_instance,
    user_profile_get_instance,
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


async def password_reset_confirm_application(
    new_password: str, session: SessionDep, current_user: Users
):
    """
    Application layer service generating reset password token
    """

    return await password_reset_confirm_instance(new_password, session, current_user)


async def user_profile_delete_application(
    username: str, session: SessionDep, current_user: Users
):
    """
    Application layer service for deleting user profile
    """

    return await user_profile_delete_instance(username, session, current_user)


async def user_profile_update_application(
    profile_data: UserProfileCreate, session: SessionDep, current_user: Users
):
    """
    Application layer service for updating user profile
    """

    return await user_profile_update_instance(profile_data, session, current_user)


async def user_profile_create_application(
    profile: UserProfileCreate, session: SessionDep, current_user: Users
):
    """
    Application layer service for creating user profile
    """

    return await user_profile_create_instance(profile, session, current_user)


async def user_profile_get_application(username: str, session: SessionDep):
    """
    Application layer service retriving user profile
    """

    return await user_profile_get_instance(username, session)
