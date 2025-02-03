from fastapi import HTTPException
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from apps.user.application.schemas import BaseResponse, UserCreateModel
from apps.user.application.service import (
    create_connection_application,
    get_connection_requests_application,
    get_followers_application,
    get_following_application,
    github_callback_application,
    handle_connection_requests_application,
    password_reset_application,
    password_reset_confirm_application,
    register_user,
    remove_follower_application,
    unfollow_user_application,
    user_profile_create_application,
    user_profile_delete_application,
    user_profile_get_application,
    user_profile_update_application,
)
from apps.user.dependency import ConnectionResponse


@patch("apps.user.application.service.github_callback_instance")
@pytest.mark.asyncio
async def test_github_callback_application(mock_github_callback_instance, session):
    mock_github_callback_instance.return_value = {
        "jwt_token": "fake_token",
        "user": {"login": "test_user"},
    }
    result = await github_callback_application(code="fake_code", session=session)
    assert result == {"jwt_token": "fake_token", "user": {"login": "test_user"}}


@pytest.mark.asyncio
@patch("apps.user.application.service.register_user_instance")
async def test_register_user(mock_register_user_instance, session):
    user_data = UserCreateModel(
        username="testuser",
        name="testuser",
        first_name="testuserfirstname",
        last_name="testuserlastname",
        email="test@example.com",
        password="29Dece200@#$%",
    )
    mock_register_user_instance.return_value = BaseResponse(
        success=True, data=user_data, message="User registered successfully!"
    )
    result = await register_user(user_data, session)
    assert result.success is True
    assert result.message == "User registered successfully!"
    assert result.data.username == "testuser"
    assert result.data.email == "test@example.com"


@pytest.mark.asyncio
@patch("apps.user.application.service.password_reset_instance")
async def test_password_reset_application(mock_password_reset_instance, mock_session):
    mock_password_reset_instance.return_value = {"message": "Password reset email sent"}
    result = await password_reset_application(session=mock_session, user="testuser")
    assert result == {"message": "Password reset email sent"}
    mock_password_reset_instance.assert_awaited_once()


@pytest.mark.asyncio
@patch("apps.user.application.service.password_reset_confirm_instance")
async def test_password_reset_confirm_application_success(
    mock_password_reset_confirm_instance, session
):
    mock_password_reset_confirm_instance.return_value = BaseResponse(
        success=True, data=None, message="Password has been reset successfully"
    )
    result = await password_reset_confirm_application(
        session=session, user="testuser", new_password="sdfvsdv"
    )
    assert result.message == "Password has been reset successfully"
    mock_password_reset_confirm_instance.assert_awaited_once()


@pytest.mark.asyncio
@patch("apps.user.application.service.user_profile_create_instance")
async def test_user_profile_create_application(
    mock_user_profile_create_instance,
    mock_session,
    mock_get_current_user,
    mock_upload_files,
    mock_user_profile_data,
):
    mock_user_profile_create_instance.return_value = BaseResponse(
        success=True,
        data=mock_user_profile_data,
        message="Profile created successfully!",
    )
    result = await user_profile_create_application(
        mock_user_profile_data["bio"],
        mock_user_profile_data["is_private_account"],
        mock_session,
        mock_get_current_user,
        mock_upload_files,
    )
    mock_user_profile_create_instance.assert_called_once_with(
        mock_user_profile_data["bio"],
        mock_user_profile_data["is_private_account"],
        mock_session,
        mock_upload_files,
        mock_get_current_user,
    )
    assert result.message == "Profile created successfully!"


@pytest.mark.asyncio
@patch("apps.user.application.service.user_profile_delete_instance")
async def test_user_profile_delete_application(
    mock_user_profile_delete_instance, session, mock_get_current_user
):
    mock_user_profile_delete_instance.return_value = BaseResponse(
        success=True, data=mock_get_current_user, message="Profile deleted successfully"
    )
    result = await user_profile_delete_application(
        mock_get_current_user.username, session, mock_get_current_user
    )
    mock_user_profile_delete_instance.assert_called_once_with(
        mock_get_current_user.username, session, mock_get_current_user
    )
    assert result.message == "Profile deleted successfully"


@pytest.mark.asyncio
@patch("apps.user.application.service.user_profile_update_instance")
async def test_user_profile_update_application(
    mock_user_profile_update_instance,
    mock_upload_files,
    session,
    mock_get_current_user,
    mock_user_profile_data,
):
    mock_user_profile_update_instance.return_value = BaseResponse(
        success=True,
        data=mock_user_profile_data,
        message="Profile updated successfully!",
    )
    result = await user_profile_update_application(
        mock_user_profile_data["bio"],
        mock_user_profile_data["is_private_account"],
        session,
        mock_get_current_user,
        mock_upload_files,
    )
    mock_user_profile_update_instance.assert_called_once_with(
        mock_user_profile_data["bio"],
        mock_user_profile_data["is_private_account"],
        session,
        mock_upload_files,
        mock_get_current_user,
    )
    assert result.message == "Profile updated successfully!"


@pytest.mark.asyncio
@patch("apps.user.application.service.user_profile_get_instance")
async def test_user_profile_get_application(
    mock_user_profile_get_instance, session, valid_profile_data
):
    mock_user_profile_get_instance.return_value = BaseResponse(
        success=True,
        message="User profile fetched successfully",
        data=valid_profile_data,
    )
    result = await user_profile_get_application(valid_profile_data["username"], session)
    mock_user_profile_get_instance.assert_called_once_with(
        valid_profile_data["username"], session
    )
    assert result.success == True
    assert result.message == "User profile fetched successfully"


@pytest.mark.asyncio
@patch("apps.user.application.service.create_connection_instance")
async def test_create_connection_application_sent(
    mock_create_connection_instance, session, mock_get_current_user
):
    mock_create_connection_instance.return_value = BaseResponse(
        success=True, data=None, message="Connection request sent"
    )
    username = "testuser1"
    result = await create_connection_application(
        username, session, mock_get_current_user
    )
    mock_create_connection_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "Connection request sent"


@pytest.mark.asyncio
@patch("apps.user.application.service.create_connection_instance")
async def test_create_connection_application_success(
    mock_create_connection_instance, session, mock_get_current_user
):
    mock_create_connection_instance.return_value = BaseResponse(
        success=True, data=None, message="Connection created"
    )
    username = "testuser1"
    result = await create_connection_application(
        username, session, mock_get_current_user
    )
    mock_create_connection_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "Connection created"


@pytest.mark.asyncio
@patch("apps.user.application.service.create_connection_instance")
async def test_create_connection_application_success_connection(
    mock_create_connection_instance, session, mock_get_current_user
):
    username = "testuser1"
    mock_create_connection_instance.return_value = BaseResponse(
        success=True,
        data=None,
        message=f"{mock_get_current_user.username} is now following {username}",
    )
    result = await create_connection_application(
        username, session, mock_get_current_user
    )
    mock_create_connection_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert (
        result.message
        == f"{mock_get_current_user.username} is now following {username}"
    )


@pytest.mark.asyncio
@patch("apps.user.application.service.create_connection_instance")
async def test_create_connection_application_withdrawn(
    mock_create_connection_instance, session, mock_get_current_user
):
    username = "testuser1"
    mock_create_connection_instance.return_value = BaseResponse(
        success=True, data=None, message="Connection request withdrawn"
    )
    result = await create_connection_application(
        username, session, mock_get_current_user
    )
    mock_create_connection_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "Connection request withdrawn"


@pytest.mark.asyncio
@patch("apps.user.application.service.create_connection_instance")
async def test_create_connection_application_already_connected(
    mock_create_connection_instance, session, mock_get_current_user
):
    username = "testuser1"
    mock_create_connection_instance.return_value = BaseResponse(
        success=True, data=None, message="User is already connected or followed"
    )
    result = await create_connection_application(
        username, session, mock_get_current_user
    )
    mock_create_connection_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "User is already connected or followed"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_connection_requests_instance")
async def test_get_connection_requests_application_no_request(
    mock_get_connection_requests_instance, session, mock_get_current_user
):
    mock_get_connection_requests_instance.return_value = BaseResponse(
        success=True, data=[], message="no requests"
    )
    result = await get_connection_requests_application(session, mock_get_current_user)
    mock_get_connection_requests_instance.assert_called_once_with(
        session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "no requests"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_connection_requests_instance")
async def test_get_connection_requests_application_list_request(
    mock_get_connection_requests_instance, session, mock_get_current_user
):
    mock_get_connection_requests_instance.return_value = BaseResponse(
        success=True,
        data=["testuser2", "testuser3"],
        message="Your connection requests",
    )
    result = await get_connection_requests_application(session, mock_get_current_user)
    mock_get_connection_requests_instance.assert_called_once_with(
        session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == "Your connection requests"


@pytest.mark.asyncio
@patch("apps.user.application.service.handle_connection_requests_instance")
async def test_handle_connection_requests_application_accepted(
    mock_handle_connection_requests_instance, session, mock_get_current_user
):
    mock_handle_connection_requests_instance.return_value = BaseResponse(
        success=True, data=None, message="Connection request accepted"
    )
    username = "testuser"
    response = ConnectionResponse.ACCEPT
    result = await handle_connection_requests_application(
        username, response, session, mock_get_current_user
    )
    mock_handle_connection_requests_instance.assert_called_once_with(
        username, response, session, mock_get_current_user
    )
    assert result.message == "Connection request accepted"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_followers_instance")
async def test_get_followers_application_no_followers(
    mock_get_followers_instance, session, mock_get_current_user
):
    mock_get_followers_instance.return_value = BaseResponse(
        success=True, data=[], message="no followers"
    )
    result = await get_followers_application(session, mock_get_current_user)
    mock_get_followers_instance.assert_called_once_with(session, mock_get_current_user)
    assert result.success == True
    assert result.message == "no followers"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_followers_instance")
async def test_get_followers_application_list_followers(
    mock_get_followers_instance, session, mock_get_current_user
):
    mock_get_followers_instance.return_value = BaseResponse(
        success=True, data=["user2,user3"], message="Your followers!"
    )
    result = await get_followers_application(session, mock_get_current_user)
    mock_get_followers_instance.assert_called_once_with(session, mock_get_current_user)
    assert result.success == True
    assert result.message == "Your followers!"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_following_instance")
async def test_get_following_application_no_following(
    mock_get_following_instance, session, mock_get_current_user
):
    mock_get_following_instance.return_value = BaseResponse(
        success=True, data=[], message="no followings"
    )
    result = await get_following_application(session, mock_get_current_user)
    mock_get_following_instance.assert_called_once_with(session, mock_get_current_user)
    assert result.success == True
    assert result.message == "no followings"


@pytest.mark.asyncio
@patch("apps.user.application.service.get_following_instance")
async def test_get_following_application_list_following(
    mock_get_following_instance, session, mock_get_current_user
):
    mock_get_following_instance.return_value = BaseResponse(
        success=True, data=["user2", "user3"], message="Your followings!"
    )
    result = await get_following_application(session, mock_get_current_user)
    mock_get_following_instance.assert_called_once_with(session, mock_get_current_user)
    assert result.success == True
    assert result.message == "Your followings!"


@pytest.mark.asyncio
@patch("apps.user.application.service.unfollow_user_instance")
async def test_unfollow_user_application_success(
    mock_unfollow, session, mock_get_current_user
):
    username = "test_user"
    mock_unfollow.return_value = BaseResponse(
        success=True, data=None, message=f"You unfollowed {username}"
    )
    result = await unfollow_user_application(username, session, mock_get_current_user)
    mock_unfollow.assert_called_once_with(username, session, mock_get_current_user)
    assert result.success == True
    assert result.message == f"You unfollowed {username}"


@pytest.mark.asyncio
@patch("apps.user.application.service.remove_follower_instance")
async def test_remove_follower_application(
    mock_remove_follower_instance, session, mock_get_current_user
):
    username = "test_follower"
    mock_remove_follower_instance.return_value = BaseResponse(
        success=True, data=None, message=f"You removed {username}"
    )
    result = await remove_follower_application(username, session, mock_get_current_user)
    mock_remove_follower_instance.assert_called_once_with(
        username, session, mock_get_current_user
    )
    assert result.success == True
    assert result.message == f"You removed {username}"


@pytest.mark.asyncio
@patch("apps.user.application.service.create_checkout_session_instance")
def test_create_checkout_failure(mock_create_checkout_session_instance, client):
    mock_create_checkout_session_instance.side_effect = HTTPException(
        status_code=400, detail="Amount must be $5"
    )
    response = client.post("/auth/create-checkout-session/", params={"amount": 400})
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["message"] == "Amount must be $5"
