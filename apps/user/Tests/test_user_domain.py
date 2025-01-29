# import pytest
# from unittest.mock import patch, MagicMock
# from apps.user.domain.service import github_callback_instance
# from apps.user.domain.models import Users
# from fastapi import HTTPException


# @patch("apps.user.domain.service.save_user_to_db")
# @patch("httpx.AsyncClient.post")
# @patch("httpx.AsyncClient.get")
# @pytest.mark.asyncio
# async def test_github_callback_instance(mock_get, mock_post, mock_save_user_to_db):
#     mock_post.return_value.json.return_value = {"access_token": "fake_access_token"}
#     mock_get.return_value.json.return_value = {"login": "test_user", "id": 12345}
#     mock_save_user_to_db.return_value = None
#     session_mock = MagicMock()
#     result = await github_callback_instance(code="fake_code", session=session_mock)

#     assert result["jwt_token"] == "fake_token"
#     assert result["user"]["login"] == "test_user"
#     mock_post.assert_called_once_with(
#         "https://github.com/login/oauth/access_token",
#         data={
#             "client_id": "GITHUB_CLIENT_ID",
#             "client_secret": "GITHUB_CLIENT_SECRET",
#             "code": "fake_code",
#         },
#         headers={"Accept": "application/json"},
#     )
#     mock_get.assert_called_once_with(
#         "https://api.github.com/user",
#         headers={"Authorization": "Bearer fake_access_token"},
#     )
#     mock_save_user_to_db.assert_called_once_with(
#         {"login": "test_user", "id": 12345}, session=session_mock
#     )


# @patch("httpx.AsyncClient.post")
# @pytest.mark.asyncio
# async def test_github_callback_instance_missing_access_token(mock_post):
#     mock_post.return_value.json.return_value = {}
#     session_mock = MagicMock()
#     with pytest.raises(HTTPException) as exc_info:
#         await github_callback_instance(code="fake_code", session=session_mock)
#     assert exc_info.value.status_code == 400
#     assert "Failed to retrieve access token" in str(exc_info.value)


