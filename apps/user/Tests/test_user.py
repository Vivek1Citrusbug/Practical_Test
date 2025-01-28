import pytest
from unittest.mock import patch

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


valid_username = "viveksoniii"
invalid_username = "nonexistentuser"

