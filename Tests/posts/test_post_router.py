from io import BytesIO
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from apps.user.application.schemas import BaseResponse
from apps.user.domain.models import Users
from apps.user.domain.service import get_current_user
from main import app


@patch("apps.posts.application.service.create_post_instance")
def test_create_post(mock_create_post_instance, client, valid_jwt_token, mock_file):

    mock_create_post_instance.return_value = BaseResponse(
        success=True,
        data={
            "id": 1,
            "post_by": "testuser",
            "title": "Test Post",
            "content": "This is a test post",
            "file_url": "test_image.jpg",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        message="Post created successfully!",
    )

    file_data = BytesIO(b"file_content")
    file_data.name = "test_image.jpg"
    response = client.post(
        "/posts/",
        files={"file": ("test_image.jpg", file_data, "image/jpeg")},
        params={"title": "Test Post", "content": "This is a test post"},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert json_response["data"]["title"] == "Test Post"
    assert json_response["data"]["content"] == "This is a test post"
    assert json_response["message"] == "Post created successfully!"


@patch("apps.posts.application.service.create_post_instance")
def test_create_post_unauthenticated(mock_create_post_instance, client):
    """
    Test case to verify that an unauthenticated user cannot create a post.
    """

    mock_create_post_instance.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
    )
    response = client.post(
        "/posts/",
        params={
            "title": "Unauthorized Post",
            "content": "This post should not be created.",
        },
    )
    assert response.status_code == 401


@patch("apps.posts.application.service.list_posts_instance")
def test_list_posts_success(mock_list_posts_instance, client):
    mock_list_posts_instance.return_value = {
        "success": True,
        "data": [
            {
                "id": 1,
                "title": "Test Post 1",
                "content": "This is a test post",
                "post_by": "testuser",
                "created_at": "2025-01-27 05:45:40.139548+00:00",
            },
            {
                "id": 2,
                "title": "Test Post 2",
                "content": "Another test post",
                "post_by": "testuser2",
                "created_at": "2025-01-28 10:12:25.123456+00:00",
            },
        ],
        "message": "Posts fetched successfully!",
    }
    response = client.get("/posts/")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["title"] == "Test Post 1"
    assert data["data"][1]["content"] == "Another test post"


@patch("apps.posts.application.service.update_post_instance")
def test_update_post_success(mock_update_post_instance, client, valid_jwt_token):
    mock_update_post_instance.return_value = {
        "success": True,
        "data": {
            "id": 1,
            "title": "Updated Post",
            "content": "This post has been updated",
            "post_by": "testuser",
            "created_at": "2025-02-03 08:30:45.567890+00:00",
        },
        "message": "Post updated successfully!",
    }
    response = client.put(
        "/posts/1/",
        params={
            "post_id": 1,
            "title": "Updated Post",
            "content": "This post has been updated",
        },
        headers=valid_jwt_token,
    )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "Updated Post"
    assert data["data"]["content"] == "This post has been updated"


@patch("apps.posts.application.service.delete_post_instance")
def test_delete_post_success(mock_delete_post_application, client, valid_jwt_token):
    mock_delete_post_application.return_value = {
        "success": True,
        "data": None,
        "message": "Post deleted successfully",
    }
    response = client.delete("/posts/1/", headers=valid_jwt_token)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Post deleted successfully"
    assert data["success"] is True


@patch("apps.posts.application.service.delete_post_instance")
def test_delete_post_unauthorized(mock_delete_post_instance, client, invalid_jwt_token):
    mock_delete_post_instance.side_effect = HTTPException(
        status_code=403, detail="Not authorized to delete this post"
    )
    response = client.delete("/posts/1/", headers=invalid_jwt_token)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Not authorized to delete this post"


@patch("apps.posts.application.service.delete_post_instance")
def test_delete_post_not_found(mock_delete_post_application, client, valid_jwt_token):
    mock_delete_post_application.side_effect = HTTPException(
        status_code=404, detail="Post not found"
    )
    response = client.delete("/posts/97987/", headers=valid_jwt_token)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Post not found"


@patch("apps.posts.application.service.delete_post_instance")
def test_delete_post_invalid_token(
    mock_delete_post_application, client, invalid_jwt_token
):
    mock_delete_post_application.side_effect = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    response = client.delete("/posts/12/", headers=invalid_jwt_token)
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["message"] == "Could not validate credentials"


@patch("apps.posts.application.service.report_post_instance")
def test_report_post(mock_report_post_instance, client):
    """Test reporting a post"""

    mock_report_post_instance.return_value = {
        "success": True,
        "message": "Post reported successfully",
    }

    response = client.post(f"/posts/1/report/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Post reported successfully"


@patch("apps.posts.application.service.report_post_instance")
def test_report_post_not_found(mock_report_post_instance, client):
    """Test reporting a non-existent post"""

    mock_report_post_instance.side_effect = HTTPException(
        status_code=404, detail="Post not found"
    )

    response = client.post("/posts/99999/report/")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Post not found"


@patch("apps.posts.application.service.create_comment_instance")
def test_create_comment(mock_create_comment_instance, client):
    """Test creating a comment on a post"""

    mock_create_comment_instance.return_value = {
        "success": True,
        "data": {
            "id": 1,
            "comment_by": "testuser",
            "content": "Test comment",
            "created_at": "2025-01-27 05:45:40.139548+00:00",
        },
        "message": "Comment created successfully",
    }

    response = client.post(
        f"/posts/1/comments/create/", params={"post_id": 1, "content": "Test comment"}
    )
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Comment created successfully"
    assert data["data"]["content"] == "Test comment"


@patch("apps.posts.application.service.list_comments_instance")
def test_list_comments(mock_list_comments_instance, client):
    """Test listing comments of a post"""

    mock_list_comments_instance.return_value = {
        "success": True,
        "data": [
            {
                "id": 1,
                "comment_by": "testuser",
                "content": "Test comment 1",
                "created_at": "2025-01-27",
            },
            {
                "id": 2,
                "comment_by": "testuser2",
                "content": "Test comment 2",
                "created_at": "2025-01-28",
            },
        ],
        "message": "Comments fetched successfully",
    }

    response = client.get(f"/posts/1/comments/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Comments fetched successfully"
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2
    assert data["data"][0]["content"] == "Test comment 1"


@patch("apps.posts.application.service.list_comments_instance")
def test_list_comments_post_not_found(mock_list_comments_instance, client):
    """Test listing comments for a non-existent post"""

    mock_list_comments_instance.side_effect = HTTPException(
        status_code=404, detail="Post not found"
    )

    response = client.get("/posts/99999/comments/")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Post not found"


@patch("apps.posts.application.service.update_comment_instance")
def test_update_comment(mock_update_comment_instance, client):
    """Test updating a comment"""

    mock_update_comment_instance.return_value = {
        "success": True,
        "message": "Comment updated successfully",
        "data": {
            "comment_by": "testuser",
            "modified_at": "2025-01-27 05:45:40.139548+00:00",
            "content": "Updated comment",
        },
    }

    response = client.put(
        f"/posts/1/comments/1/",
        params={"post_id": 1, "comment_id": 1, "content": "Updated comment"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Comment updated successfully"
    assert data["data"]["content"] == "Updated comment"


@patch("apps.posts.application.service.update_comment_instance")
def test_update_comment_not_found(mock_update_comment_instance, client):
    """Test updating a non-existent comment"""

    mock_update_comment_instance.side_effect = HTTPException(
        status_code=404, detail="Comment not found"
    )

    response = client.put(
        f"/posts/1/comments/99999/",
        params={"post_id": 1, "comment_id": 99999, "content": "Updated comment"},
    )
    assert response.status_code == 404


@patch("apps.posts.application.service.delete_comment_instance")
def test_delete_comment(mock_delete_comment_instance, client):
    """Test deleting a comment"""

    mock_delete_comment_instance.return_value = {
        "success": True,
        "message": "Comment deleted successfully",
    }

    response = client.delete(f"/posts/1/comments/2/delete/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Comment deleted successfully"


@patch("apps.posts.application.service.delete_comment_instance")
def test_delete_comment_not_found(mock_delete_comment_instance, client):
    """Test deleting a non-existent comment"""

    mock_delete_comment_instance.side_effect = HTTPException(
        status_code=404, detail="Comment not found"
    )

    response = client.delete(f"/posts/1/comments/99999/delete/")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Comment not found"


@patch("apps.posts.application.service.create_like_instance")
def test_like_post(mock_create_like_instance, client):
    """Test liking a post"""

    mock_create_like_instance.return_value = {"success": True, "message": "Post liked"}

    response = client.post(f"/posts/1/like")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Post liked"


@patch("apps.posts.application.service.create_like_instance")
def test_like_post_not_found(mock_create_like_instance, client):
    """Test liking a non-existent post"""

    mock_create_like_instance.side_effect = HTTPException(
        status_code=404, detail="Post not found"
    )

    response = client.post("/posts/99999/like")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["message"] == "Post not found"
