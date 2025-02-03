from unittest.mock import patch
from fastapi import HTTPException
import pytest
from apps.custom_admin.domain.service import get_reported_post_instance
from apps.posts.domain.models import Posts, ReportedPosts
from apps.custom_admin.domain.service import delete_post_instance
from apps.user.domain.models import Users


def test_get_reported_post_instance_as_admin(
    db_session, valid_admin_user, valid_normal_user_1, valid_normal_user_2, mock_post_1
):
    """
    Admin/Staff should be able to fetch reported posts.
    """

    admin_user = Users(**valid_admin_user)
    reports = ReportedPosts(
        post=mock_post_1.id,
        post_by=valid_normal_user_1["username"],
        reported_by=valid_normal_user_2["username"],
    )
    db_session.add_all([admin_user, reports])
    db_session.commit()
    response = get_reported_post_instance(db_session, admin_user)

    assert response.success is True
    assert response.message == "Post reported by different users!"


def test_get_reported_post_instance_as_regular_user(db_session, valid_normal_user_1):
    """
    Regular users should not be allowed to fetch reported posts.
    """
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()
    with pytest.raises(HTTPException) as excinfo:
        get_reported_post_instance(db_session, user)

    assert excinfo.value.status_code == 401


@patch("apps.custom_admin.domain.service.send_post_removal_email")
def test_delete_post_instance_success(
    mock_send_post_removal_email,
    db_session,
    valid_admin_user,
    valid_normal_user_1,
    mock_post_1,
):
    """
    Admin/Staff should be able to delete a post.
    """
    user = Users(**valid_admin_user)
    user2 = Users(**valid_normal_user_1)
    db_session.add_all([user, user2])
    db_session.commit()
    response = delete_post_instance(post_id=1, session=db_session, current_user=user)

    assert response.success is True
    assert response.data == mock_post_1


def test_delete_post_instance_post_not_found(db_session, valid_admin_user):
    """
    Deleting a non-existent post should return 404.
    """
    user = Users(**valid_admin_user)
    db_session.add(user)
    db_session.commit()
    with pytest.raises(HTTPException) as excinfo:
        delete_post_instance(post_id=9999, session=db_session, current_user=user)

    assert excinfo.value.status_code == 404


def test_delete_post_instance_as_regular_user(db_session, valid_normal_user_2):
    """
    Regular users should not be able to delete posts.
    """

    user = Users(**valid_normal_user_2)
    post = Posts(content="testing", title="testing", post_by=user.username)
    db_session.add_all([user, post])
    db_session.commit()

    with pytest.raises(HTTPException) as excinfo:
        delete_post_instance(post_id=post.id, session=db_session, current_user=user)

    assert excinfo.value.status_code == 401
