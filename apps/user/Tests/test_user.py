import pytest
from fastapi.testclient import TestClient
from main import app  
from apps.user.domain.service import create_db_and_tables, create_default_superuser
from apps.user.interface import user_router


def test_root(test_client):
    response = test_client.post("/auth/register")
    assert response.status_code == 201
    # assert response.json() == {"message": "The API is LIVE!!"}






