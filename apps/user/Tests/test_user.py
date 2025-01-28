import pytest
from fastapi.testclient import TestClient
from main import app  
from apps.user.domain.service import create_db_and_tables, create_default_superuser
from apps.user.interface import user_router

test_user_data = {
  "username": "viveksoniii",
  "name": "vivesoni",
  "first_name": "vivesonoi",
  "last_name": "strsdsdving",
  "email": "user@example.com",
  "password": "13November200@"
}


def test_register_user(client):
    response = client.post("/auth/register", json= test_user_data)
    assert response.status_code == 201
    response_json = response.json()
    assert "username" in response_json
    assert response_json["username"] == test_user_data["username"]
    assert response_json["email"] == test_user_data["email"]





