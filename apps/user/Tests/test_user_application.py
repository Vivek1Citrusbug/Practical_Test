import pytest
from unittest.mock import MagicMock, patch

from apps.user.application.service import (
    github_callback_application,
    password_reset_application,
)


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
