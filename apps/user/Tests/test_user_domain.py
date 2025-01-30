import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlmodel import select
from fastapi import HTTPException
from apps.user.domain.service import user_profile_delete_instance
from apps.user.domain.models import Profile, Users
from apps.user.application.schemas import BaseResponse


@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_success(mock_remove_profile_data):
    """Test deleting a profile successfully"""
    session = MagicMock()
    user = Users(username="testuser", is_staff=False, is_superuser=False)
    profile = Profile(username="testuser")

    session.exec.return_value.first.return_value = profile  # Mock profile retrieval

    result = await user_profile_delete_instance("testuser", session, user)

    session.delete.assert_called_once_with(profile)
    session.commit.assert_called_once()
    mock_remove_profile_data.assert_awaited_once_with(profile)

    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Profile deleted successfully"


@pytest.mark.asyncio
async def test_user_profile_delete_not_found():
    """Test deleting a profile that does not exist"""
    session = MagicMock()
    session.exec.return_value.first.return_value = None  # No profile found
    user = Users(username="testuser", is_staff=False, is_superuser=False)

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_delete_instance("unknownuser", session, user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Profile not found"


@pytest.mark.asyncio
async def test_user_profile_delete_unauthorized():
    """Test unauthorized profile deletion"""
    session = MagicMock()
    profile = Profile(username="testuser")
    session.exec.return_value.first.return_value = profile
    user = Users(username="anotheruser", is_staff=False, is_superuser=False)  # Unauthorized user

    with pytest.raises(HTTPException) as exc_info:
        await user_profile_delete_instance("testuser", session, user)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "You are not authorized to perform this task"


















@pytest.mark.asyncio
@patch("apps.user.domain.service.remove_profile_data", new_callable=AsyncMock)
async def test_user_profile_delete_admin_success(mock_remove_profile_data, mock_session,valid_profile_data,valid_admin_user):
    """Test admin deleting a user profile using a mocked session"""

    profile = Profile(**valid_profile_data)
    mock_session.exec.return_value.first.return_value = profile
    admin_user = Users(**valid_admin_user)
    print(admin_user)
    result = await user_profile_delete_instance("testuser", mock_session, admin_user)
    mock_session.delete.assert_called_once_with(profile) 
    mock_session.commit.assert_called_once()  
    mock_remove_profile_data.assert_awaited_once_with(profile)  
    assert isinstance(result, BaseResponse)
    assert result.success is True
    assert result.message == "Profile deleted successfully"