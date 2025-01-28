from io import BytesIO
import pytest
from unittest.mock import MagicMock, patch


def test_register_user(client, valid_user_data):
    response = client.post("/auth/register", json=valid_user_data)
    assert response.status_code == 200
    response_json = response.json()
    assert "username" in response_json
    assert response_json["username"] == valid_user_data["username"]
    assert response_json["email"] == valid_user_data["email"]


def test_register_user_missing_username(client, invalid_user_data_missing_username):
    response = client.post("/auth/register", json=invalid_user_data_missing_username)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert "username" in str(response_json["detail"])


def test_register_user_invalid_email(client, invalid_user_data_invalid_email):
    response = client.post("/auth/register", json=invalid_user_data_invalid_email)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert "email" in str(response_json["detail"])


def test_register_user_weak_password(client, invalid_user_data_weak_password):
    response = client.post("/auth/register", json=invalid_user_data_weak_password)
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert "password" in str(response_json["detail"])


def test_github_login(client):
    response = client.get("/auth/github/login")
    assert response.status_code == 200
    assert "auth_url" in response.json()
    assert "https://github.com/login/oauth/authorize" in response.json()["auth_url"]


@patch("apps.user.interface.user_router.github_callback_application")
def test_github_callback(mock_github_callback_application, client):
    mock_github_callback_application.return_value = {
        "jwt_token": "fake_token",
        "user": {"login": "test_user"},
    }
    response = client.get("/auth/github/callback?code=fake_code")
    assert response.status_code == 200
    assert response.json() == {
        "jwt_token": "fake_token",
        "user": {"login": "test_user"},
    }


@patch("apps.user.interface.user_router.password_reset_application")
def test_password_reset_request(mock_password_reset_application, client):
    mock_password_reset_application.return_value = {
        "message": "Password reset email sent"
    }
    response = client.post(
        "/auth/password-reset/testuser/", params={"username": "testuser"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent"}



# @patch("apps.user.interface.user_router.user_profile_create_application")
# def test_user_profile_create(mock_user_profile_create_application, client):
#     mock_user_profile_create_application.return_value = {
#         "bio": "test bio",
#         "profile_picture":"path-to-minio-server",
#         "is_private_account":True,
#         "created_at":"date",
#     }
#     response = client.post(
#         "/auth/password-reset/testuser/", params={"username": "testuser"}
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Password reset email sent"}


def test_create_profile_success(mock_get_current_user, mock_user_profile_data,client):
    file_data = BytesIO(b"file_content")
    file_data.name = "test_image.jpg"
    
    response = client.post(
        "/auth/profiles/",
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={
            "bio": mock_user_profile_data["bio"],
            "is_private_account": mock_user_profile_data["is_private_account"],
        },
        headers={"Authorization": f"Bearer mock_token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "bio" in data
    assert data["bio"] == mock_user_profile_data["bio"]
    assert "is_private_account" in data
    assert data["is_private_account"] == mock_user_profile_data["is_private_account"]

