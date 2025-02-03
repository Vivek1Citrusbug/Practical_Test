from fastapi import HTTPException
from apps.posts.domain.models import Posts
from apps.user.Tests.conftest import *
from apps.posts.domain.service import create_comment_instance, create_post_instance, delete_post_instance, get_followers, list_comments_instance, list_posts_instance, report_post_instance, update_post_instance


def test_create_post_instance_success(db_session,valid_normal_user_1, mock_file):
    """Test successful post creation"""

    response = create_post_instance(
        session=mock_session,
        title="Test Title",
        content="Test Content",
        current_user=valid_normal_user_1,
        file=mock_file,
    )

    assert response.success is True
    assert response.message == "Post created successfully!"


def test_create_post_instance_fail(db_session, valid_normal_user_1):
    """Test failure due to database error"""

    db_session.commit.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc:
        create_post_instance(
            session=mock_session,
            title="Test Title",
            content="Test Content",
            current_user=valid_normal_user_1,
            file=None,
        )

    assert "Database error" in str(exc.value)


def test_list_posts_instance_success(mock_session, mock_user):
    """Test listing posts successfully"""

    mock_session.exec.return_value.all.return_value = [
        Posts(id=1, title="Test Post", content="Content", post_by="test_user")
    ]

    response = list_posts_instance(session=mock_session, current_user=mock_user)

    assert response.success is True
    assert len(response.data) > 0
    assert response.message == "Post returned successfully"


def test_list_posts_instance_user_not_found(db_session, valid_normal_user_1):
    """Test listing posts when username is not found"""

    db_session.exec.return_value.first.return_value = None
    with pytest.raises(Exception) as exc:
        list_posts_instance(session=mock_session, current_user=valid_normal_user_1, username="fake_user")
    assert "User not found" in str(exc.value)


def test_list_posts_instance_unverified_user(mock_session, valid_normal_user_1):
    """Test listing posts for unverified users"""

    mock_session.exec.return_value.all.return_value = []
    response = list_posts_instance(session=mock_session, current_user=valid_normal_user_1)
    assert response.success is True
    assert len(response.data) == 0


def test_get_followers_success(mock_session, mock_user):
    """Test retrieving followers successfully"""

    mock_session.exec.side_effect = [
        MagicMock(all=lambda: ["user1", "user2"]),
        MagicMock(all=lambda: ["user3"]),
    ]

    result = get_followers(mock_session, mock_user)

    assert set(result) == {"user1", "user2", "user3"}


def test_get_followers_empty(mock_session, mock_user):
    """Test retrieving followers when there are none"""

    mock_session.exec.side_effect = [
        MagicMock(all=lambda: []),
        MagicMock(all=lambda: []),
    ]

    result = get_followers(mock_session, mock_user)

    assert result == []


def test_update_post_instance_success(mock_session, mock_user, mock_post, mock_file):
    """Test successful post update"""
    
    mock_session.get.return_value = mock_post
    mock_session.commit.return_value = None

    response = update_post_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_user,
        title="Updated Title",
        content="Updated Content",
        file=mock_file,
    )

    assert response.success is True
    assert response.message == "Post updated successfully!"
    assert response.data.title == "Updated Title"
    assert response.data.content == "Updated Content"


def test_update_post_instance_not_found(mock_session, mock_user):
    """Test post update when post is not found"""

    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        update_post_instance(
            post_id=99,
            session=mock_session,
            current_user=mock_user,
            title="Updated Title",
            content="Updated Content",
            file=None,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_update_post_instance_not_owner(mock_session, mock_user, mock_post):
    """Test post update when user is not the owner"""

    mock_post.post_by = "another_user"
    mock_session.get.return_value = mock_post

    with pytest.raises(HTTPException) as exc:
        update_post_instance(
            post_id=1,
            session=mock_session,
            current_user=mock_user,
            title="Updated Title",
            content="Updated Content",
            file=None,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not the owner of this post"


### Test Cases for delete_post_instance ###

def test_delete_post_instance_success(mock_session, mock_user, mock_post):
    """Test successful post deletion"""

    mock_session.get.return_value = mock_post
    mock_session.commit.return_value = None
    mock_session.delete.return_value = None

    response = delete_post_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_user,
    )

    assert response.success is True
    assert response.message == "Post delete successfully"
    assert response.data == mock_post


def test_delete_post_instance_not_found(mock_session, mock_user):
    """Test post deletion when post is not found"""

    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        delete_post_instance(
            post_id=99,
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_delete_post_instance_not_authorized(mock_session, mock_user, mock_post):
    """Test post deletion when user is not authorized"""

    mock_post.post_by = "another_user"
    mock_session.get.return_value = mock_post

    with pytest.raises(HTTPException) as exc:
        delete_post_instance(
            post_id=1,
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not authorized to perform this task."


def test_delete_post_instance_admin_override(mock_session, mock_admin_user, mock_post):
    """Test admin can delete any post"""

    mock_session.get.return_value = mock_post
    mock_session.commit.return_value = None
    mock_session.delete.return_value = None

    response = delete_post_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_admin_user,
    )

    assert response.success is True
    assert response.message == "Post delete successfully"


def test_report_post_instance_success(mock_session, mock_user, mock_post):
    """Test successful post reporting"""

    mock_session.exec.return_value.first.return_value = mock_post
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    response = report_post_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_user,
    )

    assert response.success is True
    assert response.message == "Post reported successfully!"


def test_report_post_instance_post_not_found(mock_session, mock_user):
    """Test reporting a non-existent post"""

    mock_session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        report_post_instance(
            post_id=99,
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_report_post_instance_own_post(mock_session, mock_user, mock_post):
    """Test user trying to report their own post"""

    mock_post.post_by = "test_user"
    mock_session.exec.return_value.first.return_value = mock_post

    with pytest.raises(HTTPException) as exc:
        report_post_instance(
            post_id=1,
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not permitted to report your own posts."


def test_report_post_instance_unverified_user_not_following(mock_session, mock_unverified_user, mock_post):
    """Test unverified user trying to report a post without following the author"""

    mock_session.exec.return_value.first.return_value = mock_post

    with patch("app.services.post_service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            report_post_instance(
                post_id=1,
                session=mock_session,
                current_user=mock_unverified_user,
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "You must follow the post author to report post."


### Test Cases for create_comment_instance ###

def test_create_comment_instance_success(mock_session, mock_user, mock_post):
    """Test successful comment creation"""

    mock_session.exec.return_value.first.return_value = mock_post
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    response = create_comment_instance(
        post_id=1,
        content="New Comment",
        session=mock_session,
        current_user=mock_user,
    )

    assert response.success is True
    assert response.message == "Comment posted successfully!"
    assert response.data.content == "New Comment"


def test_create_comment_instance_post_not_found(mock_session, mock_user):
    """Test commenting on a non-existent post"""

    mock_session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        create_comment_instance(
            post_id=99,
            content="New Comment",
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_create_comment_instance_unverified_user_not_following(mock_session, mock_unverified_user, mock_post):
    """Test unverified user trying to comment without following the author"""

    mock_session.exec.return_value.first.return_value = mock_post

    with patch("app.services.post_service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            create_comment_instance(
                post_id=1,
                content="New Comment",
                session=mock_session,
                current_user=mock_unverified_user,
            )

        assert exc.value.status_code == 403
        assert exc.value.detail == "You must follow the post author to create comment."


### Test Cases for list_comments_instance ###

def test_list_comments_instance_success(mock_session, mock_user, mock_post, mock_comment):
    """Test successful retrieval of comments"""

    mock_session.exec.return_value.first.return_value = mock_post
    mock_session.exec.return_value.all.return_value = [mock_comment]

    response = list_comments_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_user,
    )

    assert response.success is True
    assert response.message == "Comments on this post"
    assert len(response.data) == 1


def test_list_comments_instance_post_not_found(mock_session, mock_user):
    """Test listing comments on a non-existent post"""

    mock_session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        list_comments_instance(
            post_id=99,
            session=mock_session,
            current_user=mock_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_list_comments_instance_no_comments(mock_session, mock_user, mock_post):
    """Test listing comments when no comments are available"""

    mock_session.exec.return_value.first.return_value = mock_post
    mock_session.exec.return_value.all.return_value = []

    response = list_comments_instance(
        post_id=1,
        session=mock_session,
        current_user=mock_user,
    )

    assert response.success is True
    assert response.message == "No comment to show"
    assert response.data == []


def test_list_comments_instance_unverified_user_not_following(mock_session, mock_unverified_user, mock_post):
    """Test unverified user trying to list comments without following the author"""

    mock_session.exec.return_value.first.return_value = mock_post

    with patch("app.services.post_service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            list_comments_instance(
                post_id=1,
                session=mock_session,
                current_user=mock_unverified_user,
            )

        assert exc.value.status_code == 403
        assert exc.value.detail == "You must follow the post author to list comments."


def test_update_comment_success(get_token):
    """Test updating a comment successfully."""
    response = client.put(
        f"/posts/{POST_ID}/comments/{COMMENT_ID}",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"content": "Updated comment content"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Comment updated successfully!"


def test_update_comment_not_found(get_token):
    """Test updating a non-existent comment."""
    response = client.put(
        f"/posts/{POST_ID}/comments/9999",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"content": "Trying to update a non-existent comment"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_update_comment_without_following(get_token):
    """Test updating a comment without following the post author."""
    response = client.put(
        f"/posts/{POST_ID}/comments/{COMMENT_ID}",
        headers={"Authorization": f"Bearer {get_token}"},
        json={"content": "Updated without following"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "You must follow the post author to update comment."


# ================================
# Test Cases for Deleting Comments
# ================================

def test_delete_comment_success(get_token):
    """Test deleting a comment successfully."""
    response = client.delete(f"/posts/{POST_ID}/comments/{COMMENT_ID}", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Comment deleted successfully"


def test_delete_comment_not_found(get_token):
    """Test deleting a non-existent comment."""
    response = client.delete(f"/posts/{POST_ID}/comments/9999", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_delete_comment_not_owned(get_token):
    """Test deleting a comment that the user does not own."""
    response = client.delete(f"/posts/{POST_ID}/comments/{COMMENT_ID}", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not authorized to perform this task."


def test_admin_delete_any_comment(get_admin_token):
    """Test that an admin can delete any comment."""
    response = client.delete(f"/posts/{POST_ID}/comments/{COMMENT_ID}", headers={"Authorization": f"Bearer {get_admin_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Comment deleted successfully"


# ================================
# Test Cases for Liking a Post
# ================================

def test_like_post_success(get_token):
    """Test liking a post successfully."""
    response = client.post(f"/posts/{POST_ID}/like", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Post liked"


def test_unlike_post_success(get_token):
    """Test unliking a post successfully."""
    response = client.post(f"/posts/{POST_ID}/like", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["message"] == "Post unliked"


def test_like_non_existent_post(get_token):
    """Test liking a non-existent post."""
    response = client.post("/posts/9999/like", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_like_post_without_following(get_token):
    """Test liking a post without following the author."""
    response = client.post(f"/posts/{POST_ID}/like", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "You must follow the post author to like this post."