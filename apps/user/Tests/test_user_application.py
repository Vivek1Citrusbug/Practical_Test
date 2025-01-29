import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from apps.user.application.service import (
    create_connection_application,
    get_connection_requests_application,
    get_followers_application,
    get_following_application,
    github_callback_application,
    handle_connection_requests_application,
    password_reset_application,
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
async def test_github_callback_application(mock_github_callback_instance):
    mock_github_callback_instance.return_value = {
        "jwt_token": "fake_token",
        "user": {"login": "test_user"},
    }
    session_mock = MagicMock()
    result = await github_callback_application(code="fake_code", session=session_mock)
    assert result == {"jwt_token": "fake_token", "user": {"login": "test_user"}}


@pytest.mark.asyncio
@patch("apps.user.application.service.password_reset_instance")
async def test_password_reset_application(mock_password_reset_instance):
    mock_password_reset_instance.return_value = {"message": "Password reset email sent"}
    result = await password_reset_application(session=MagicMock(), user="testuser")
    assert result == {"message": "Password reset email sent"}
    mock_password_reset_instance.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_profile_create_application(mock_session, mock_get_current_user, mock_upload_files):
    with patch('apps.user.application.service.user_profile_create_instance', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = "Profile Created"
        bio = "New user bio"
        is_private_account = True
        result = await user_profile_create_application(bio, is_private_account, mock_session, mock_get_current_user, mock_upload_files)
        mock_create.assert_called_once_with(bio, is_private_account, mock_session, mock_upload_files, mock_get_current_user)
        assert result == "Profile Created"


@pytest.mark.asyncio
async def test_user_profile_delete_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.user_profile_delete_instance', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = "Profile Deleted"
        username = "testuser"
        result = await user_profile_delete_application(username, mock_session, mock_get_current_user)
        mock_delete.assert_called_once_with(username, mock_session, mock_get_current_user)
        assert result == "Profile Deleted"

@pytest.mark.asyncio
async def test_user_profile_update_application(mock_session, mock_get_current_user, mock_upload_files):
    with patch('apps.user.application.service.user_profile_update_instance', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = "Profile Updated"
        bio = "Updated bio"
        is_private_account = False
        result = await user_profile_update_application(bio, is_private_account, mock_session, mock_get_current_user, mock_upload_files)
        mock_update.assert_called_once_with(bio, is_private_account, mock_session, mock_upload_files, mock_get_current_user)
        assert result == "Profile Updated"
    
@pytest.mark.asyncio
async def test_user_profile_get_application(mock_session):
    with patch('apps.user.application.service.user_profile_get_instance', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"username": "test_user", "bio": "bio text"}
        username = "testuser"
        result = await user_profile_get_application(username, mock_session)
        mock_get.assert_called_once_with(username, mock_session)
        assert result == {"username": "test_user", "bio": "bio text"}


@pytest.mark.asyncio
async def test_create_connection_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.create_connection_instance', new_callable=AsyncMock) as mock_create_connection:
        mock_create_connection.return_value = {
            "message":"Connection request sent"
        }
        
        username = "testuser"
        result = await create_connection_application(username, mock_session, mock_get_current_user)
        
        mock_create_connection.assert_called_once_with(username, mock_session, mock_get_current_user)
        assert result["message"] == "Connection request sent"


@pytest.mark.asyncio
async def test_get_connection_requests_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.get_connection_requests_instance', new_callable=AsyncMock) as mock_get_requests:
        mock_get_requests.return_value = [{"username": "test_user", "status": "pending"}]

        result = await get_connection_requests_application(mock_session, mock_get_current_user)

        mock_get_requests.assert_called_once_with(mock_session, mock_get_current_user)
        assert result == [{"username": "test_user", "status": "pending"}]


@pytest.mark.asyncio
async def test_handle_connection_requests_application_accepted(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.handle_connection_requests_instance', new_callable=AsyncMock) as mock_handle:
        mock_handle.return_value = "request accepted"

        username = "testuser"
        response = ConnectionResponse.ACCEPT
        result = await handle_connection_requests_application(username, response, mock_session, mock_get_current_user)

        mock_handle.assert_called_once_with(username, response, mock_session, mock_get_current_user)
        assert result == "request accepted"


@pytest.mark.asyncio
async def test_get_followers_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.get_followers_instance', new_callable=AsyncMock) as mock_get_followers:
        mock_get_followers.return_value = ["testfollower",]

        result = await get_followers_application(mock_session, mock_get_current_user)

        mock_get_followers.assert_called_once_with(mock_session, mock_get_current_user)
        assert result == ["testfollower",]


@pytest.mark.asyncio
async def test_get_following_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.get_following_instance', new_callable=AsyncMock) as mock_get_following:
        mock_get_following.return_value = ["testfollowing"]
        result = await get_following_application(mock_session, mock_get_current_user)

        mock_get_following.assert_called_once_with(mock_session, mock_get_current_user)
        assert result == ["testfollowing",]


@pytest.mark.asyncio
async def test_unfollow_user_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.unfollow_user_instance', new_callable=AsyncMock) as mock_unfollow:
        mock_unfollow.return_value = "Unfollowed User"
        username = "test_user"
        result = await unfollow_user_application(username, mock_session, mock_get_current_user)
        mock_unfollow.assert_called_once_with(username, mock_session, mock_get_current_user)
        assert result == "Unfollowed User"


@pytest.mark.asyncio
async def test_remove_follower_application(mock_session, mock_get_current_user):
    with patch('apps.user.application.service.remove_follower_instance', new_callable=AsyncMock) as mock_remove_follower:
        mock_remove_follower.return_value = "Follower Removed"
        username = "test_follower"
        result = await remove_follower_application(username, mock_session, mock_get_current_user)
        mock_remove_follower.assert_called_once_with(username, mock_session, mock_get_current_user)
        assert result == "Follower Removed"