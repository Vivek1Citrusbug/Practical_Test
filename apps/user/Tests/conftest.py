import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session
from main import app  # Import your FastAPI app
from database import get_session

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
