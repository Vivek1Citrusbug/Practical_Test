from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Annotated
from fastapi import Depends, UploadFile
from httpx import patch
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session
from apps.user.domain.models import Connections
from apps.user.domain.service import create_access_token, get_current_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from main import app  # Import your FastAPI app
from database import get_session
from unittest.mock import AsyncMock, MagicMock
from apps.user.application.schemas import Token
from database import SessionDep

TEST_SQLITE_URL = "sqlite:///./test_blogpost_database.db"
test_engine = create_engine(TEST_SQLITE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# @pytest.fixture()
# def session():
#     SQLModel.metadata.drop_all(bind=test_engine)
#     SQLModel.metadata.create_all(bind=test_engine)

#     db = TestingSessionLocal()
#     try:
#         yield db
#         db.commit()
#     finally:
#         db.close()


# @pytest.fixture()
# def client(session):
#     def override_get_session():
#         with Session(test_engine) as db_session:
#             yield db_session

#     app.dependency_overrides[get_session] = override_get_session
#     app.dependency_overrides[SessionDep] = override_get_session
#     yield TestClient(app)

@pytest.fixture()
def session():
    """Fixture to create a test database session and rollback after each test."""
    SQLModel.metadata.drop_all(bind=test_engine)  
    SQLModel.metadata.create_all(bind=test_engine) 
    
    db = TestingSessionLocal()
    try:
        yield db  
        db.commit()
    finally:
        db.rollback()  
        db.close()

@pytest.fixture(scope="session")
def client(session):
    """Fixture to override FastAPI dependencies and provide a test client."""

    def override_get_session():
        yield session  

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[SessionDep] = override_get_session  

    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def db_session():
    """Create a test database session with SQLModel compatibility"""
    engine = create_engine(TEST_SQLITE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)  
    with Session(engine) as session:
        yield session  
        session.rollback()
        session.close() 

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
def valid_profile_data():
    return {
        "id": 1,
        "bio": "test bio",
        "profile_picture": "test_image.jpg",
        "is_private_account": True,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": True,
        "username": "testuser",
    }


@pytest.fixture
def valid_normal_profile_data_1():
    return {
        "id": 2,
        "bio": "test bio",
        "profile_picture": "test_image.jpg",
        "is_private_account": True,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": True,
        "username": "normaluser1",
    }


@pytest.fixture
def valid_normal_profile_data_2():
    return {
        "id": 3,
        "bio": "test bio",
        "profile_picture": "test_image.jpg",
        "is_private_account": True,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": True,
        "username": "normaluser2",
    }


@pytest.fixture
def valid_normal_profile_data_3():
    return {
        "id": 10,
        "bio": "test bio",
        "profile_picture": "test_image.jpg",
        "is_private_account": False,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": True,
        "username": "normaluser3",
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
    """Mocked session that does not interact with a real database"""
    session = MagicMock()
    session.exec = MagicMock()
    session.delete = MagicMock()
    session.commit = MagicMock()
    return session


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


@pytest.fixture
def valid_admin_user():
    return {
        "id": 2,
        "username": "testadmin",
        "name": "testadmin",
        "firs_tname": "testadminfirstname",
        "last_name": "testadminlastname",
        "is_superuser": True,
        "is_staff": True,
        "email": "testadmin@example.com",
        "password": "13November200@",
        "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
        "is_verified": True,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": True,
    }


@pytest.fixture
def valid_normal_user_1():
    return {
        "id": 3,
        "username": "normaluser1",
        "name":"normaluser1",
        "first_name": "testnormaluserfirstname",
        "last_name": "testnormaluserlastname",
        "is_superuser": False,
        "is_staff": False,
        "email": "testnormaluser@example.com",
        "password": "13November200@",
        "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
        "is_verified": False,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": False,
    }


@pytest.fixture
def valid_normal_user_3():
    return {
        "id": 10,
        "username": "normaluser3",
        "name":"normaluser3",
        "first_name": "testnormaluserfirstname",
        "last_name": "testnormaluserlastname",
        "is_superuser": False,
        "is_staff": False,
        "email": "testnormaluser3@example.com",
        "password": "13November200@",
        "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
        "is_verified": False,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": False,
    }

@pytest.fixture
def valid_normal_user_2():
    return {
        "id": 4,
        "username": "normaluser2",
        "name": "normaluser2",
        "firs_tname": "testnormaluserfirstname2",
        "last_name": "testnormaluserlastname2",
        "is_superuser": False,
        "is_staff": False,
        "email": "testnormaluser2@example.com",
        "password": "13November200@",
        "password_reset_token": "$2b$12$DpW5KsltB0SO39qlB8ERJu8ytF3FHWxtOQ2.EEqbBNp0Iba.S.h4G",
        "is_verified": False,
        "created_at": "2025-01-27 05:45:40.139548+00:00",
        "modified_at": "2025-01-27 05:45:40.139548+00:00",
        "is_active": False,
    }

@pytest.fixture(scope="module")
def mock_get_current_user():
    return {
        "id": 10,
        "username": "testuser",
        "name": "testuser",
        "firs_tname": "testuserfirstname",
        "last_name": "testuserlastname",
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
    access_token = create_access_token(
        data={"sub": mock_get_current_user["username"]},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@pytest.fixture
def invalid_jwt_token():
    """Generate an expired JWT token."""
    expired_time = datetime.now(UTC) - timedelta(minutes=10)
    access_token = jwt.encode(
        {"sub": "random_user", "exp": expired_time}, SECRET_KEY, algorithm=ALGORITHM
    )
    return Token(access_token=access_token, token_type="bearer")


@pytest.fixture
def mock_upload_files():
    return [MagicMock(spec=UploadFile)]


@pytest.fixture()
def mock_connection_request(session):
    connection = Connections(
        follower="user1",
        following="testuser",
        status=2,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )
    session.add(connection)
    session.commit()
    return connection

@pytest.fixture
def mock_file():
    file = UploadFile(filename="test_image.jpg", file=BytesIO(b"fake_image_data"))
    return file


@pytest.fixture
def mock_file_unsupported():
    file = UploadFile(filename="test_image.jiff", file=BytesIO(b"fake_image_data"))
    return file
