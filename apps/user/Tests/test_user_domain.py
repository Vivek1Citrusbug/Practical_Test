import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlmodel import select
from fastapi import HTTPException
from apps.user.dependency import ConnectionResponse
from apps.user.domain.service import (
    create_checkout_session_instance,
    create_connection_instance,
    get_connection_requests_instance,
    get_followers_instance,
    get_following_instance,
    github_callback_instance,
    handle_connection_requests_instance,
    password_reset_confirm_instance,
    password_reset_instance,
    remove_follower_instance,
    unfollow_user_instance,
    user_profile_create_instance,
    user_profile_delete_instance,
    user_profile_get_instance,
    user_profile_update_instance,
)
from apps.user.domain.models import Connections, Profile, Users
from apps.user.application.schemas import BaseResponse
from database import SessionDep


@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_success(
    mock_remove_profile_data,
    db_session,
    valid_normal_user_1,
    valid_normal_profile_data_1,
):
    """Test deleting a profile successfully"""

    user = Users(**valid_normal_user_1)
    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    result = await user_profile_delete_instance(user.username, db_session, user)
    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Profile deleted successfully"
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_profile_not_found(
    mock_remove_profile_data,
    db_session,
    valid_normal_user_1,
    valid_normal_profile_data_1,
):
    """Test deleting a profile successfully"""

    user = Users(**valid_normal_user_1)
    with pytest.raises(Exception) as exc_info:
        await user_profile_delete_instance(user.username, db_session, user)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_unauthorized(
    mock_remove_profile_data,
    db_session,
    valid_normal_profile_data_1,
    valid_normal_user_2,
):
    """Test unauthorized profile deletion"""

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    user = Users(**valid_normal_user_2)
    with pytest.raises(HTTPException) as exc_info:
        await user_profile_delete_instance(profile.username, db_session, user)
    assert exc_info.value.status_code == 401
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_admin_success(
    mock_remove_profile_data, db_session, valid_normal_profile_data_2, valid_admin_user
):
    """Test admin deleting a user profile using a mocked session"""

    profile = Profile(**valid_normal_profile_data_2)
    db_session.add(profile)
    db_session.commit()
    admin_user = Users(**valid_admin_user)
    result = await user_profile_delete_instance(
        profile.username, db_session, admin_user
    )
    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Profile deleted successfully"
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_password_reset_success(db_session, valid_normal_user_1):
    """Test successful password reset token generation and email sending"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with patch("apps.user.domain.service.mail_service", return_value=True):
        response = await password_reset_instance(db_session, user.username)

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Password reset email sent"

    updated_user = db_session.exec(
        select(Users).where(Users.username == user.username)
    ).first()
    assert updated_user.password_reset_token is not None
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_password_reset_user_not_found(db_session):
    """Test password reset when the user does not exist"""

    with pytest.raises(HTTPException) as exc_info:
        await password_reset_instance(db_session, "non_existent_user")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_password_reset_email_fail(db_session, valid_normal_user_1):
    """Test password reset when email sending fails"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with patch("apps.user.domain.service.mail_service", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await password_reset_instance(db_session, user.username)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error sending email"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_password_reset_confirm_success(db_session, valid_normal_user_1):
    """Test successful password reset confirmation with valid token"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    user.password_reset_token = "valid_token"
    db_session.commit()

    with patch("apps.user.domain.service.verify_reset_token", return_value=user.email):
        response = await password_reset_confirm_instance(
            "26Dec200@#$", db_session, user.username
        )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Password has been reset successfully"

    updated_user = db_session.exec(
        select(Users).where(Users.username == user.username)
    ).first()
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_password_reset_confirm_user_not_found(db_session):
    """Test password reset confirmation when user is not found"""

    with pytest.raises(HTTPException) as exc_info:
        await password_reset_confirm_instance(
            "26Dec200@#$", db_session, "non_existent_user"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_token(db_session, valid_normal_user_1):
    """Test password reset confirmation with invalid or expired token"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    user.password_reset_token = "expired_or_invalid_token"
    db_session.commit()

    with patch("apps.user.domain.service.verify_reset_token", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await password_reset_confirm_instance(
                "26Dec200@#$", db_session, user.username
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid or expired token"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_password_format(
    db_session, valid_normal_user_1
):
    """Test password reset confirmation with invalid password format"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    user.password_reset_token = "valid_token"
    db_session.commit()

    with patch("apps.user.domain.service.verify_reset_token", return_value=user.email):
        with pytest.raises(ValueError) as exc_info:
            await password_reset_confirm_instance("short", db_session, user.username)

    assert str(exc_info.value) == "Password must contain at least one digit."
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_success(db_session, valid_normal_user_1, mock_file):
    """Test creating a profile successfully with allowed file uploads"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with patch("apps.user.domain.service.upload_to_minio", return_value="mock_url"):
        response = await user_profile_create_instance(
            bio="This is a bio",
            is_private_account=False,
            session=db_session,
            files=[mock_file],
            current_user=user,
        )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Profile created successfully!"

    new_profile = db_session.exec(
        select(Profile).where(Profile.username == user.username)
    ).first()
    assert new_profile is not None
    assert new_profile.bio == "This is a bio"
    assert new_profile.profile_picture == "mock_url"
    db_session.delete(user)
    db_session.delete(new_profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_admin_error(db_session, valid_admin_user, mock_file):
    """Test that admins cannot create profiles"""

    admin_user = Users(**valid_admin_user)
    db_session.add(admin_user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_create_instance(
            bio="This is a bio",
            is_private_account=False,
            session=db_session,
            files=[mock_file],
            current_user=admin_user,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Admins cannot have profiles"
    db_session.delete(admin_user)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_already_exists(
    db_session, valid_normal_user_1, mock_file
):
    """Test that a user cannot create more than one profile"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    existing_profile = Profile(
        bio="Existing profile bio",
        profile_picture="existing_url",
        is_private_account=False,
        username=user.username,
    )
    db_session.add(existing_profile)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_create_instance(
            bio="New bio",
            is_private_account=True,
            session=db_session,
            files=[mock_file],
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User already has a profile"
    db_session.delete(user)
    db_session.delete(existing_profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_unsupported_file_type(
    db_session, valid_normal_user_1, mock_file_unsupported
):
    """Test that unsupported file types are rejected"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_create_instance(
            bio="This is a bio",
            is_private_account=False,
            session=db_session,
            files=[mock_file_unsupported],
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_file_upload_error(
    db_session, valid_normal_user_1, mock_file
):
    """Test error during file upload to MinIO"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with patch(
        "apps.user.domain.service.upload_to_minio",
        side_effect=Exception("MinIO upload error"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await user_profile_create_instance(
                bio="This is a bio",
                is_private_account=False,
                session=db_session,
                files=[mock_file],
                current_user=user,
            )

    assert exc_info.value.status_code == 500
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_create_general_error(
    db_session, valid_normal_user_1, mock_file
):
    """Test general error during file processing"""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with patch(
        "apps.user.domain.service.upload_to_minio",
        side_effect=Exception("Unexpected error"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await user_profile_create_instance(
                bio="This is a bio",
                is_private_account=False,
                session=db_session,
                files=[mock_file],
                current_user=user,
            )

    assert exc_info.value.status_code == 500
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_get_success(
    db_session,
    valid_normal_profile_data_1,
):
    """Test get a profile successfully"""

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    result = await user_profile_get_instance(profile.username, db_session)
    assert isinstance(result, BaseResponse)
    assert result.success is True
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_profile_get_not_found_error(
    db_session, valid_normal_profile_data_1, mock_file
):
    """Test profile not found"""

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_get_instance("nonexistinguser", db_session)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_profile_update_success(
    db_session, valid_normal_user_1, valid_normal_profile_data_1
):
    """Test: Successful profile update with bio and private account change"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()

    response = await user_profile_update_instance(
        bio="Updated bio",
        is_private_account=True,
        session=db_session,
        files=None,
        current_user=user,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Profile updated successfully!"
    updated_profile = db_session.exec(
        select(Profile).where(Profile.username == user.username)
    ).first()
    assert updated_profile.bio == "Updated bio"
    assert updated_profile.is_private_account is True
    db_session.delete(user)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_profile_update_with_files(
    db_session, valid_normal_user_1, valid_normal_profile_data_1, mock_file
):
    """Test: Successful profile update with bio and files uploaded"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()

    with patch(
        "apps.user.domain.service.upload_to_minio", return_value="http://fakeurl.com"
    ):
        response = await user_profile_update_instance(
            bio="Updated bio with image",
            is_private_account=False,
            session=db_session,
            files=[mock_file],
            current_user=user,
        )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Profile updated successfully!"
    updated_profile = db_session.exec(
        select(Profile).where(Profile.username == user.username)
    ).first()
    assert updated_profile.bio == "Updated bio with image"
    assert "http://fakeurl.com" in updated_profile.profile_picture
    db_session.delete(user)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_profile_not_found(db_session, valid_normal_user_1):
    """Test: Profile not found"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_update_instance(
            bio="Updated bio",
            is_private_account=True,
            session=db_session,
            files=None,
            current_user=user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_unsupported_file_type(
    db_session, valid_normal_user_1, mock_file_unsupported, valid_normal_profile_data_1
):
    """Test: Unsupported file type uploaded"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_update_instance(
            bio="Updated bio",
            is_private_account=True,
            session=db_session,
            files=[mock_file_unsupported],
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in str(exc_info.value)
    db_session.delete(user)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_minio_upload_error(
    db_session, valid_normal_user_1, mock_file, valid_normal_profile_data_1
):
    """Test: Error uploading the file to MinIO"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()

    with patch(
        "apps.user.domain.service.upload_to_minio",
        side_effect=Exception("Error uploading file"),
    ):
        with pytest.raises(Exception) as exc_info:
            await user_profile_update_instance(
                bio="Updated bio",
                is_private_account=True,
                session=db_session,
                files=[mock_file],
                current_user=user,
            )

    assert "Error uploading file" in str(exc_info.value)
    db_session.delete(user)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_profile_update_no_changes(
    db_session, valid_normal_user_1, valid_normal_profile_data_1
):
    """Test: No changes provided"""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_1)
    db_session.add(profile)
    db_session.commit()

    response = await user_profile_update_instance(
        bio=None,
        is_private_account=None,
        session=db_session,
        files=None,
        current_user=user,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Profile updated successfully!"
    db_session.delete(user)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_create_connection_success_public_account(
    db_session, valid_normal_user_1, valid_normal_user_3, valid_normal_profile_data_3
):
    """Test: Successfully create a connection with a public account"""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_3)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_3)
    db_session.add(profile)
    db_session.commit()

    response = await create_connection_instance(
        username=user2.username,
        session=db_session,
        current_user=user1,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Connection created"
    connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username,
        )
    ).first()
    assert connection is not None
    assert connection.status == 1

    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_create_connection_success_private_account(
    db_session, valid_normal_user_3, valid_normal_user_2, valid_normal_profile_data_2
):
    """Test: Successfully send a connection request to a private account"""
    user1 = Users(**valid_normal_user_3)
    user2 = Users(**valid_normal_user_2)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_2)
    db_session.add(profile)
    db_session.commit()

    response = await create_connection_instance(
        username=user2.username,
        session=db_session,
        current_user=user1,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Connection request sent"
    connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username,
        )
    ).first()
    assert connection is not None
    assert connection.status == 2
    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(profile)
    db_session.commit()


@pytest.mark.asyncio
async def test_connection_request_update_status(
    db_session, valid_normal_user_1, valid_normal_user_2, valid_normal_profile_data_2
):
    """Test: Successfully update the connection request status"""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_2)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_2)
    db_session.add(profile)
    db_session.commit()

    connection = Connections(
        follower=user1.username,
        following=user2.username,
        status=0,
    )
    db_session.add(connection)
    db_session.commit()

    response = await create_connection_instance(
        username=user2.username,
        session=db_session,
        current_user=user1,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Connection request sent"
    updated_connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username,
        )
    ).first()
    assert updated_connection.status == 2
    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(profile)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_withdraw_connection_request(
    db_session, valid_normal_user_1, valid_normal_user_2, valid_normal_profile_data_2
):
    """Test: Successfully withdraw a connection request"""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_2)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_2)
    db_session.add(profile)
    db_session.commit()

    connection = Connections(
        follower=user1.username,
        following=user2.username,
        status=2,
    )
    db_session.add(connection)
    db_session.commit()

    response = await create_connection_instance(
        username=user2.username,
        session=db_session,
        current_user=user1,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "Connection request withdrawn"
    withdrawn_connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username,
        )
    ).first()
    assert withdrawn_connection.status == 0
    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(profile)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_self_connection_request(db_session, valid_normal_user_1):
    """Test: User cannot send a connection request to themselves"""
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await create_connection_instance(
            username=user1.username,
            session=db_session,
            current_user=user1,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User can not sent request to themselves"
    db_session.delete(user1)
    db_session.commit()


@pytest.mark.asyncio
async def test_user_not_found(db_session, valid_normal_user_1):
    """Test: User to follow does not exist"""
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await create_connection_instance(
            username="nonexistinguser",
            session=db_session,
            current_user=user1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found."
    db_session.delete(user1)
    db_session.commit()


@pytest.mark.asyncio
async def test_profile_not_found(db_session, valid_normal_user_1):
    """Test: Profile for the user to follow does not exist"""
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await create_connection_instance(
            username="user2",
            session=db_session,
            current_user=user1,
        )

    assert exc_info.value.status_code == 404
    db_session.delete(user1)
    db_session.commit()


@pytest.mark.asyncio
async def test_connection_already_exists(
    db_session, valid_normal_user_1, valid_normal_user_3, valid_normal_profile_data_3
):
    """Test: Connection already exists between users"""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_3)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    profile = Profile(**valid_normal_profile_data_3)
    db_session.add(profile)
    db_session.commit()

    existing_connection = Connections(
        follower=user1.username,
        following=user2.username,
        status=1,
    )
    db_session.add(existing_connection)
    db_session.commit()

    response = await create_connection_instance(
        username=user2.username,
        session=db_session,
        current_user=user1,
    )

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == "User is already connected or followed"
    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(profile)
    db_session.delete(existing_connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_unfollow_user_success(
    db_session, valid_normal_user_1, valid_normal_user_2
):
    """Test successful unfollow action."""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_2)
    db_session.add_all([user1, user2])
    db_session.commit()

    connection = Connections(
        follower=user1.username, following=user2.username, status=1
    )
    db_session.add(connection)
    db_session.commit()

    response = await unfollow_user_instance(user2.username, db_session, user1)

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.message == f"You unfollowed {user2.username}"

    updated_connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username,
        )
    ).first()

    assert updated_connection.status == 0
    db_session.delete(user1)
    db_session.delete(user2)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_unfollow_user_not_following(
    db_session, valid_normal_user_1, valid_normal_user_2
):
    """Test unfollowing a user who is not being followed."""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_2)
    db_session.add_all([user1, user2])
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await unfollow_user_instance(user2.username, db_session, user1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not following to this user."

    db_session.delete(user1)
    db_session.delete(user2)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_connection_requests_success(db_session, valid_normal_user_1):
    """
    Test when user has pending connection requests.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    connection1 = Connections(follower="user1", following=user.username, status=2)
    connection2 = Connections(follower="user2", following=user.username, status=2)

    db_session.add_all([connection1, connection2])
    db_session.commit()

    response = await get_connection_requests_instance(db_session, user)

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.data == ["user1", "user2"]
    assert response.message == "Your connection requests"
    db_session.delete(user)
    db_session.delete(connection1)
    db_session.delete(connection2)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_connection_requests_no_requests(db_session, valid_normal_user_1):
    """
    Test when user has no pending connection requests.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    response = await get_connection_requests_instance(db_session, user)

    assert isinstance(response, BaseResponse)
    assert response.success is True
    assert response.data == []
    assert response.message == "no requests"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_accept_connection_request(
    db_session, valid_normal_user_1, valid_normal_user_2
):
    """
    Test successful acceptance of a pending connection request.
    """
    user = Users(**valid_normal_user_1)
    sender = Users(**valid_normal_user_2)
    db_session.add_all([user, sender])
    db_session.commit()

    connection = Connections(
        follower=sender.username, following=user.username, status=2
    )
    db_session.add(connection)
    db_session.commit()

    response = ConnectionResponse(value="accept")
    result = await handle_connection_requests_instance(
        sender.username, response, db_session, user
    )

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Connection request accepted"
    db_session.delete(user)
    db_session.delete(sender)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_reject_connection_request(
    db_session, valid_normal_user_1, valid_normal_user_2
):
    """
    Test successful rejection of a pending connection request.
    """
    user = Users(**valid_normal_user_1)
    sender = Users(**valid_normal_user_2)
    db_session.add_all([user, sender])
    db_session.commit()

    connection = Connections(
        follower=sender.username, following=user.username, status=2
    )
    db_session.add(connection)
    db_session.commit()

    response = ConnectionResponse(value="reject")
    result = await handle_connection_requests_instance(
        sender.username, response, db_session, user
    )

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Connection request rejected"
    db_session.delete(user)
    db_session.delete(sender)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_connection_request_not_found(db_session, valid_normal_user_1):
    """
    Test when there is no pending connection request.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    response = ConnectionResponse(value="accept")

    with pytest.raises(HTTPException) as exc_info:
        await handle_connection_requests_instance(
            "non_existing_user", response, db_session, user
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Connection request not found"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_followers_with_followers(
    db_session, valid_normal_user_1, valid_normal_user_2
):
    """
    Test case where user has followers.
    """
    user = Users(**valid_normal_user_1)
    follower = Users(**valid_normal_user_2)

    db_session.add_all([user, follower])
    db_session.commit()

    connection = Connections(
        follower=follower.username, following=user.username, status=1
    )
    db_session.add(connection)
    db_session.commit()

    result = await get_followers_instance(db_session, user)

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.data == [follower.username]
    assert result.message == "Your followers!"

    db_session.delete(user)
    db_session.delete(follower)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_followers_no_followers(db_session, valid_normal_user_1):
    """
    Test case where user has no followers.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    result = await get_followers_instance(db_session, user)

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.data == []
    assert result.message == "no followers"
    db_session.delete(user)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_following_with_followings(
    db_session, valid_normal_user_3, valid_normal_user_1
):
    """
    Test case where user follows others.
    """
    user = Users(**valid_normal_user_3)
    following_user = Users(**valid_normal_user_1)

    db_session.add_all([user, following_user])
    db_session.commit()

    connection = Connections(
        follower=user.username, following=following_user.username, status=1
    )
    db_session.add(connection)
    db_session.commit()

    result = await get_following_instance(db_session, user)

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.data == [following_user.username]
    assert result.message == "Your followings!"

    db_session.delete(user)
    db_session.delete(following_user)
    db_session.delete(connection)
    db_session.commit()


@pytest.mark.asyncio
async def test_get_following_no_followings(db_session, valid_normal_user_1):
    """
    Test case where user is not following anyone.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    result = await get_following_instance(db_session, user)

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.data == []
    assert result.message == "no followings"

    db_session.delete(user)
    db_session.commit()




@pytest.mark.asyncio
async def test_remove_existing_follower(db_session,valid_normal_user_2,valid_normal_user_3):
    """Test successfully removing an existing follower"""
    
    user1 = Users(**valid_normal_user_2)
    user2 = Users(**valid_normal_user_3)
    db_session.add_all([user1, user2])
    db_session.commit()

    connection = Connections(
        follower=user1.username,following = user2.username, status=1
    )
    db_session.add(connection)
    db_session.commit()

    response = await remove_follower_instance(username=user1.username, session=db_session, current_user=user2)
    assert response.success is True
    assert response.message == f"You removed {user1.username}"

    deleted_connection = db_session.exec(
        select(Connections).where(
            Connections.follower == user1.username,
            Connections.following == user2.username
        )
    ).first()
    assert deleted_connection is None

@pytest.mark.asyncio
async def test_remove_non_existent_follower(db_session,valid_normal_user_1):
    """Test removing a follower that does not exist"""
    
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as excinfo:
       await remove_follower_instance(username="random_user", session=db_session, current_user=user)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Follower not found"


@pytest.mark.asyncio
async def test_create_checkout_session_instance_valid_amount():
    mock_session = MagicMock()
    mock_stripe_session = MagicMock()
    mock_stripe_session.url = "https://fakecheckouturl.com"
    
    with patch("stripe.checkout.Session.create", return_value=mock_stripe_session):
        response = await create_checkout_session_instance(amount=500, session=mock_session)
        
        assert response.success is True
        assert response.data == mock_stripe_session.url
        assert response.message == "Your checkout url!"


@pytest.mark.asyncio
async def test_create_checkout_session_instance_invalid_amount():
    mock_session = MagicMock()
    
    with pytest.raises(HTTPException) as exc_info:
        await create_checkout_session_instance(amount=1000, session=mock_session)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Amount must be $5"

@pytest.mark.asyncio
async def test_create_checkout_session_instance_stripe_failure():
    mock_session = MagicMock()
    with patch("stripe.checkout.Session.create", side_effect=Exception("Stripe API failure")):
        with pytest.raises(HTTPException) as exc_info:
            await create_checkout_session_instance(amount=500, session=mock_session)
        assert exc_info.value.status_code == 400
        assert "Error creating checkout session: Stripe API failure" in exc_info.value.detail

@pytest.mark.asyncio
async def test_success_url_with_session_id():
    mock_session = MagicMock()
    mock_stripe_session = MagicMock()
    mock_stripe_session.url = "https://fakecheckouturl.com/after-checkout?session_id="

    with patch("stripe.checkout.Session.create", return_value=mock_stripe_session):
        response = await create_checkout_session_instance(amount=500, session=mock_session)

        assert "session_id=" in response.data
        assert response.data == "https://fakecheckouturl.com/after-checkout?session_id="



@pytest.mark.asyncio
async def test_github_callback_instance_success():
    mock_session = MagicMock()
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "fake_access_token"}
    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"login": "testuser", "id": 123}
    mock_save_user_to_db = AsyncMock()

    with patch("httpx.AsyncClient.post", return_value=mock_token_response):
        with patch("httpx.AsyncClient.get", return_value=mock_user_response):
            with patch("apps.user.domain.service.save_user_to_db", mock_save_user_to_db):
                response = await github_callback_instance(code="valid_code", session=mock_session)
                
                assert response.success is True
                assert "jwt_token" in response.data
                assert response.data["user"]["login"] == "testuser"
                mock_save_user_to_db.assert_awaited_once()  


@pytest.mark.asyncio
async def test_github_callback_instance_invalid_code():
    mock_session = MagicMock()
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"error": "invalid_grant"}

    with patch("httpx.AsyncClient.post", return_value=mock_token_response):
        with pytest.raises(HTTPException) as exc_info:
            await github_callback_instance(code="invalid_code", session=mock_session)
        
        assert exc_info.value.status_code == 400
        assert "Failed to retrieve access token" in exc_info.value.detail