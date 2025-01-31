from unittest.mock import MagicMock, patch
import pytest
from apps.posts.domain.service import create_post_instance
from fastapi.testclient import TestClient
from apps.posts.domain.models import Posts

def test_fixture_imported(db_session):
    assert db_session is not None  # Or any other fixture you imported