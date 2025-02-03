from unittest.mock import patch

from fastapi import HTTPException
import pytest
from apps.custom_admin.application.service import (
    get_reported_post_application,
    delete_post_application,
)
from apps.posts.domain.models import ReportedPosts
from apps.user.domain.models import Users


def test_get_reported_post_application_success(
    db_session, valid_admin_user, mock_post_1, valid_normal_user_1, valid_normal_user_2
):
    """
    Test successful retrieval of reported posts by an admin/staff user.
    """

    admin_user = Users(**valid_admin_user)
    reports = ReportedPosts(
        post=mock_post_1.id,
        post_by=valid_normal_user_1["username"],
        reported_by=valid_normal_user_2["username"],
    )
    db_session.add_all([admin_user, reports])
    db_session.commit()
    response = get_reported_post_application(
        session=db_session, current_user=admin_user
    )
    assert response.success == True


def test_get_reported_post_application_unauthorized(db_session, valid_normal_user_1):
    """
    Test unauthorized access for a non-admin user.
    """

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_reported_post_application(session=db_session, current_user=user)

    assert exc_info.value.status_code == 401


def test_delete_post_application_success(db_session, valid_admin_user, mock_post_1):
    """
    Test successful post deletion by an admin.
    """
    user = Users(**valid_admin_user)
    db_session.add(user)
    db_session.commit()

    response = delete_post_application(post_id=1, session=db_session, current_user=user)
    assert response.success == True


def test_delete_post_application_unauthorized(
    db_session, valid_normal_user_1, mock_post_1
):
    """
    Test unauthorized post deletion attempt by a non-admin user.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        delete_post_application(post_id=1, session=db_session, current_user=user)

    assert exc_info.value.status_code == 401


def test_delete_post_application_not_found(db_session, valid_admin_user):
    """
    Test unauthorized post deletion attempt by a non-admin user.
    """
    user = Users(**valid_admin_user)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        delete_post_application(post_id=55, session=db_session, current_user=user)

    assert exc_info.value.status_code == 404
