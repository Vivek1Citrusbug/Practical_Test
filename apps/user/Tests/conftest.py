from datetime import timedelta
from fastapi import UploadFile
from httpx import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session
from apps.user.domain.service import create_access_token,get_current_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from main import app  # Import your FastAPI app
from database import get_session
from unittest.mock import AsyncMock, MagicMock
from apps.user.application.schemas import Token
from database import SessionDep

TEST_SQLITE_URL = "sqlite:///./test_blogpost_database.db"
test_engine = create_engine(TEST_SQLITE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def session():
    SQLModel.metadata.drop_all(bind=test_engine)
    SQLModel.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_session():
        with session as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)


@pytest.fixture
def valid_user_data():
    return {
        "username": "viveksoniii",
        "name": "viveksoni",
        "first_name": "vivesonoi",
        "last_name": "strsdsdving",
        "email": "user@example.com",
        "password": "13November200@",
    }


@pytest.fixture
def invalid_user_data_missing_username():
    return {
        "name": "viveksoni",
        "first_name": "vivek",
        "last_name": "soni",
        "email": "viveksoni@example.com",
        "password": "13November200@",
    }


@pytest.fixture
def invalid_user_data_invalid_email():
    return {
        "username": "viveksoniii",
        "name": "viveksoni",
        "first_name": "vivek",
        "last_name": "soni",
        "email": "invalid-email-format",
        "password": "13November200@",
    }


@pytest.fixture
def invalid_user_data_weak_password():
    return {
        "username": "viveksoniii",
        "name": "viveksoni",
        "first_name": "vivek",
        "last_name": "soni",
        "email": "viveksoni@example.com",
        "password": "12345",
    }


@pytest.fixture
def mock_session():
    return MagicMock(SessionDep)

mock_user = {
    "id": 1,
    "username": "testuser",
    "firstname": "testuserfirstname",
    "lastname": "testuserlastname",
    "is_superuser": True,
    "is_staff": True,
    "email": "testuser@example.com",
    "password": "13November200@",
    "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
    "is_verified": True,
    "created_at": "2025-01-27 05:45:40.139548+00:00",
    "modified_at": "2025-01-27 05:45:40.139548+00:00",
    "is_active": True,
}


@pytest.fixture(scope="module")
def mock_get_current_user():
    return {
        "id": 1,
        "username": "testuser",
        "firstname": "testuserfirstname",
        "lastname": "testuserlastname",
        "is_superuser": 1,
        "is_staff": 1,
        "email": "testuser@example.com",
        "password": "13November200@",
        "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
        "is_verified": 1,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": 1,
    }

@pytest.fixture(autouse=True)
def override_dependency(mock_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user


@pytest.fixture(scope="module")
def mock_user_profile_data():
    return {
        "bio": "This is a test bio",
        "is_private_account": True,
    }

@pytest.fixture
def valid_jwt_token(mock_get_current_user):
    """Generate a JWT token using the app's actual token creation function."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": mock_get_current_user['username']}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@pytest.fixture
def mock_upload_files():
    return [MagicMock(spec=UploadFile)]

    
    
