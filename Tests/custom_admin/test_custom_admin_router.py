from unittest.mock import patch
from fastapi import HTTPException

from apps.posts.domain.models import ReportedPosts
from apps.user.application.schemas import BaseResponse
from apps.user.domain.models import Users


@patch("apps.custom_admin.application.service.get_reported_post_instance")
def test_get_reported_posts_success(
    mock_get_reported_post_instance,
    db_session,
    valid_admin_user,
    valid_jwt_token,
    client,
    mock_post_1,
    valid_normal_user_1,
    valid_normal_user_2,
):
    """
    Test if an admin user can retrieve reported posts.
    """

    admin_user = Users(**valid_admin_user)
    reports = ReportedPosts(
        post=mock_post_1.id,
        post_by=valid_normal_user_1["username"],
        reported_by=valid_normal_user_2["username"],
    )
    db_session.add_all([admin_user, reports])
    db_session.commit()
    mock_get_reported_post_instance.return_value = BaseResponse(
        success=True, data=reports, message="Post reported by different users!"
    )
    response = client.get("/custom_admin/reported_posts/", headers=valid_jwt_token)
    print(response.json())
    assert response.status_code == 200


@patch("apps.custom_admin.application.service.get_reported_post_instance")
def test_get_reported_posts_unauthorized(
    mock_get_reported_post_instance, invalid_jwt_token, client
):
    """
    Test if a non-admin user gets unauthorized error when accessing reported posts.
    """

    mock_get_reported_post_instance.side_effect = HTTPException(
        status_code=401, detail="Unauthorized access"
    )
    response = client.get("/custom_admin/reported_posts/", headers=invalid_jwt_token)

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Unauthorized access"


@patch("apps.custom_admin.application.service.delete_post_instance")
def test_delete_post_success(
    mock_delete_post_instance, valid_admin_user, client, valid_jwt_token
):
    """
    Test if an admin user can delete a post successfully.
    """

    mock_delete_post_instance.return_value = {"message": "Post deleted successfully."}
    response = client.delete("/custom_admin/post/1/delete", headers=valid_jwt_token)
    assert response.status_code == 200


@patch("apps.custom_admin.application.service.delete_post_instance")
def test_delete_post_not_found(
    mock_delete_post_instance, valid_admin_user, valid_jwt_token, client
):
    """
    Test if deleting a non-existent post returns 404.
    """

    mock_delete_post_instance.side_effect = HTTPException(
        status_code=404, detail="Post not found."
    )
    response = client.delete("/custom_admin/post/99999/delete", headers=valid_jwt_token)
    assert response.status_code == 404


@patch("apps.custom_admin.application.service.delete_post_instance")
def test_delete_post_unauthorized(mock_delete_post_instance, invalid_jwt_token, client):
    """
    Test if a non-admin user is forbidden from deleting posts.
    """

    mock_delete_post_instance.side_effect = HTTPException(
        status_code=401, detail="Unauthorized action"
    )
    response = client.delete("/custom_admin/post/1/delete", headers=invalid_jwt_token)
    assert response.status_code == 401
