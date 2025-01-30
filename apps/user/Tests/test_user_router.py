from io import BytesIO
from fastapi import HTTPException
import pytest
from unittest.mock import MagicMock, patch

from apps.user.application.schemas import UserProfilePublic


def test_register_user(client, valid_user_data):
    response = client.post("/auth/register", json=valid_user_data)
    assert response.status_code == 200
    response_json = response.json()
    assert "username" in response_json["data"]
    assert response_json["data"]["username"] == valid_user_data["username"]
    assert response_json["data"]["email"] == valid_user_data["email"]


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
    assert "auth_url" in response.json()["data"]
    assert (
        "https://github.com/login/oauth/authorize"
        in response.json()["data"]["auth_url"]
    )


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


@patch("apps.user.interface.user_router.user_profile_create_application")
def test_create_profile_success(
    mock_user_profile_create_application,
    mock_get_current_user,
    mock_user_profile_data,
    client,
    valid_jwt_token,
):
    file_data = BytesIO(b"file_content")
    file_data.name = "test_image.jpg"
    mock_user_profile_create_application.return_value = {
        "success": True,
        "data": {
            "bio": "This is a test bio",
            "is_private_account": True,
            "profile_picture": "test_image.jpg",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        "message": "User registrered successfully!",
    }
    response = client.post(
        "/auth/profiles/",
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={
            "bio": mock_user_profile_data["bio"],
            "is_private_account": mock_user_profile_data["is_private_account"],
        },
        headers={"Authorization": f"Bearer {valid_jwt_token.access_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "bio" in data["data"]
    assert data["data"]["bio"] == mock_user_profile_data["bio"]
    assert "is_private_account" in data["data"]
    assert (
        data["data"]["is_private_account"]
        == mock_user_profile_data["is_private_account"]
    )


@patch("apps.user.interface.user_router.user_profile_get_application")
def test_get_profile_success(mock_user_profile_get_application, client):
    mock_user_profile_get_application.return_value = {
        "success": True,
        "data": {
            "bio": "This is a test bio",
            "is_private_account": True,
            "profile_picture": "test_image.jpg",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        "message": "User registrered successfully!",
    }
    response = client.get("/auth/profiles/testuser/")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["bio"] == "This is a test bio"
    assert data["data"]["is_private_account"] is True


@patch("apps.user.interface.user_router.user_profile_update_application")
def test_update_profile_application_success(
    mock_user_profile_update_application,
    client,
    valid_jwt_token,
    mock_user_profile_data,
):
    file_data = BytesIO(b"file_content_updated")
    file_data.name = "test_image.jpg"
    mock_user_profile_update_application.return_value = {
        "success": True,
        "data": {
            "bio": "updated bio",
            "is_private_account": False,
            "profile_picture": "test_image.jpg",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        "message": "Profile updated successfully!",
    }
    response = client.put(
        "/auth/profiles/testuser/",
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        data={
            "bio": "updated bio",
            "is_private_account": False,
        },
        headers=valid_jwt_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["bio"] == "updated bio"
    assert data["data"]["is_private_account"] is False


@patch("apps.user.application.service.user_profile_delete_instance")
def test_user_profile_delete_success(
    mock_user_profile_delete_instance, client, valid_jwt_token
):
    """Test successful profile deletion"""

    # Mock successful response from application layer
    mock_user_profile_delete_instance.return_value = {
        "success": True,
        "data": {
            "bio": "This is test bio",
            "is_private_account": True,
            "profile_picture": "test_image.jpg",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        "message": "Profile deleted successfully",
    }

    response = client.delete(
        "/auth/profiles/testuser",
        headers=valid_jwt_token,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Profile deleted successfully"
    assert data["success"] is True


@patch("apps.user.application.service.user_profile_delete_instance")
def test_user_profile_delete_unauthorized(
    mock_user_profile_delete_instance, client, valid_jwt_token
):
    """Test unauthorized profile deletion"""

    mock_user_profile_delete_instance.side_effect = HTTPException(
        status_code=403, detail="Not authorized to delete this profile"
    )

    response = client.delete(
        "/auth/profiles/anotheruser",
        headers=valid_jwt_token,
    )

    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Not authorized to delete this profile"


@patch("apps.user.application.service.user_profile_delete_instance")
def test_user_profile_delete_not_found(
    mock_user_profile_delete_instance, client, valid_jwt_token
):
    """Test deleting a non-existent profile"""

    mock_user_profile_delete_instance.side_effect = HTTPException(
        status_code=404, detail="Profile not found"
    )
    response = client.delete(
        "/auth/profiles/nonexistentuser",
        headers=valid_jwt_token,
    )
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Profile not found"


@patch("apps.user.application.service.user_profile_delete_instance")
def test_user_profile_delete_invalid_token(
    mock_user_profile_delete_instance, client, invalid_jwt_token
):
    """Test profile deletion with an invalid token"""
    mock_user_profile_delete_instance.side_effect = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    response = client.delete(
        "/auth/profiles/testuser",
        headers=invalid_jwt_token,
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error"]["message"] == "Could not validate credentials"
