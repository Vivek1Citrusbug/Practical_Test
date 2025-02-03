from unittest.mock import patch
from fastapi import HTTPException
import pytest
from apps.posts.domain.models import Comments, Posts
from apps.posts.domain.service import create_comment_instance, create_post_instance, delete_post_instance, get_followers, list_comments_instance, list_posts_instance, report_post_instance, update_post_instance
from apps.user.domain.models import Connections, Users


def test_create_post_instance_success(db_session, valid_normal_user_1, mock_file):
    """Test successful post creation."""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()
    
    response = create_post_instance(
        session=db_session,
        title="Test Title",
        content="Test Content",
        current_user=user,
        file=mock_file,
    )

    assert response.success is True
    assert response.message == "Post created successfully!"
    assert response.data.title == "Test Title"


def test_create_post_instance_fail(db_session, valid_normal_user_1, mocker):
    """Test failure due to database error."""
    
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    mocker.patch.object(db_session, "commit", side_effect=Exception("Database error"))

    with pytest.raises(Exception) as exc:
        create_post_instance(
            session=db_session,
            title="Test Title",
            content="Test Content",
            current_user=user,
            file=None,
        )

    assert "Database error" in str(exc.value)


def test_list_posts_instance_success(db_session, valid_normal_user_1):
    """Test listing posts successfully."""
    
    user = Users(**valid_normal_user_1)
    post = Posts(id=1, title="Test Post", content="Content", post_by=user.username)
    db_session.add_all([post,user])
    db_session.commit()

    response = list_posts_instance(session=db_session, current_user=user)

    assert response.success is True
    assert len(response.data) > 0
    assert response.data[0].title == "Test Post"
    assert response.message == "Post returned successfully"


def test_list_posts_instance_user_not_found(db_session, valid_normal_user_1):
    """Test listing posts when username is not found."""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(Exception) as exc:
        list_posts_instance(session=db_session, current_user=user, username="fake_user")

    assert "User not found" in str(exc.value)


def test_list_posts_instance_unverified_user(db_session, valid_normal_user_1):
    """Test listing posts for unverified users."""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    
    response = list_posts_instance(session=db_session, current_user=user)

    assert response.success is True
    assert len(response.data) == 0


def test_update_post_instance_success(db_session, valid_normal_user_1, mock_post_1, mock_file):
    """Test successful post update."""

    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    response = update_post_instance(
        post_id=mock_post_1.id,
        session=db_session,
        current_user=user,
        title="Updated Title",
        content="Updated Content",
        file=mock_file,
    )

    assert response.success is True
    assert response.message == "Post updated successfully!"
    assert response.data.title == "Updated Title"
    assert response.data.content == "Updated Content"


def test_update_post_instance_not_found(db_session, valid_normal_user_1):
    """Test post update when post is not found."""
    user = Users(**valid_normal_user_1)
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        update_post_instance(
            post_id=99, 
            session=db_session,
            current_user=user,
            title="Updated Title",
            content="Updated Content",
            file=None,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_update_post_instance_not_owner(db_session, valid_normal_user_1, mock_post_1, valid_normal_user_2):
    """Test post update when user is not the owner."""
    user1 = Users(**valid_normal_user_1)
    user2 = Users(**valid_normal_user_2)
    db_session.add_all([user1,user2])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        update_post_instance(
            post_id=mock_post_1.id,
            session=db_session,
            current_user=user2,  # Different user
            title="Updated Title",
            content="Updated Content",
            file=None,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not the owner of this post"

## Test Cases for delete_post_instance ###

def test_delete_post_instance_success(db_session, valid_normal_user_1, mock_post_1):
    """Test successful post deletion"""

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    response = delete_post_instance(
        post_id=1,
        session=db_session,
        current_user=user1,
    )

    assert response.success is True
    assert response.message == "Post delete successfully"
    assert response.data == mock_post_1


def test_delete_post_instance_not_found(db_session, valid_normal_user_1):
    """Test post deletion when post is not found"""
    
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        delete_post_instance(
            post_id=99,
            session=db_session,
            current_user=user1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_delete_post_instance_not_authorized(db_session, valid_normal_user_2, mock_post_1):
    """Test post deletion when user is not authorized"""

    user2 = Users(**valid_normal_user_2)
    db_session.add(user2)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        delete_post_instance(
            post_id=1,
            session=db_session,
            current_user=user2,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not authorized to perform this task."


def test_delete_post_instance_admin_override(db_session, valid_admin_user, mock_post_1):
    """Test admin can delete any post"""
    
    admin = Users(**valid_admin_user)
    db_session.add(admin)
    db_session.commit()
    
    response = delete_post_instance(
        post_id=1,
        session=db_session,
        current_user=admin,
    )

    assert response.success is True
    assert response.message == "Post delete successfully"


def test_report_post_instance_success(db_session,valid_normal_user_1 ,valid_normal_user_2, mock_post_1):
    """Test successful post reporting"""
    
    user2 = Users(**valid_normal_user_2)
    connection  = Connections(follower=user2.username,following=valid_normal_user_1["username"],status=1)
    db_session.add_all([user2,connection])
    db_session.commit()

    response = report_post_instance(
        post_id=1,
        session=db_session,
        current_user=user2,
    )

    assert response.success is True
    assert response.message == "Post reported successfully!"


def test_report_post_instance_post_not_found(db_session, valid_normal_user_1):
    """Test reporting a non-existent post"""

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        report_post_instance(
            post_id=99,
            session=db_session,
            current_user=user1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_report_post_instance_own_post(db_session, valid_normal_user_1, mock_post_1):
    """Test user trying to report their own post"""
     
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        report_post_instance(
            post_id=1,
            session=db_session,
            current_user=user1,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not permitted to report your own posts."


def test_report_post_instance_unverified_user_not_following(db_session, valid_normal_user_2, mock_post_1):
    """Test unverified user trying to report a post without following the author"""
    
    user2 = Users(**valid_normal_user_2)
    db_session.add(user2)
    db_session.commit()
    
    with patch("apps.posts.domain.service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            report_post_instance(
                post_id=1,
                session=db_session,
                current_user=user2,
            )

        assert exc.value.status_code == 404
        assert exc.value.detail == "You must follow the post author to report post."


### Test Cases for create_comment_instance ###

def test_create_comment_instance_success(db_session, valid_normal_user_1, mock_post_1):
    """Test successful comment creation"""

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    response = create_comment_instance(
        post_id=1,
        content="New Comment",
        session=db_session,
        current_user=user1,
    )

    assert response.success is True
    assert response.message == "Comment posted successfully!"
    assert response.data.content == "New Comment"


def test_create_comment_instance_post_not_found(db_session, valid_normal_user_1):
    """Test commenting on a non-existent post"""
    
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        create_comment_instance(
            post_id=99,
            content="New Comment",
            session=db_session,
            current_user=user1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_create_comment_instance_unverified_user_not_following(db_session, valid_normal_user_2, mock_post_1):
    """Test unverified user trying to comment without following the author"""
    
    user1 = Users(**valid_normal_user_2)
    db_session.add(user1)
    db_session.commit()
    
    with patch("apps.posts.domain.service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            create_comment_instance(
                post_id=1,
                content="New Comment",
                session=db_session,
                current_user=user1,
            )

        assert exc.value.status_code == 403
        assert exc.value.detail == "You must follow the post author to create comment."


### Test Cases for list_comments_instance ###

def test_list_comments_instance_success(db_session, valid_normal_user_1, mock_post_1):
    """Test successful retrieval of comments"""

    user1 = Users(**valid_normal_user_1)
    comment1 = Comments(post=mock_post_1.id,comment_by=user1.username,content="testcomment")
    db_session.add_all([user1,comment1])
    db_session.commit()
    

    response = list_comments_instance(
        post_id=1,
        session=db_session,
        current_user=user1,
    )

    assert response.success is True
    assert response.message == "Comments on this post"
    assert len(response.data) == 1


def test_list_comments_instance_post_not_found(db_session, valid_normal_user_1):
    """Test listing comments on a non-existent post"""

    user1 = Users(**valid_normal_user_1)
    db_session.add_all([user1])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        list_comments_instance(
            post_id=99,
            session=db_session,
            current_user=user1,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Post not found"


def test_list_comments_instance_no_comments(db_session, valid_normal_user_1, mock_post_1):
    """Test listing comments when no comments are available"""

    user1 = Users(**valid_normal_user_1)
    db_session.add_all([user1])
    db_session.commit()

    response = list_comments_instance(
        post_id=1,
        session=db_session,
        current_user=user1,
    )

    assert response.success is True
    assert response.message == "No comment to show"
    assert response.data == []


def test_list_comments_instance_unverified_user_not_following(db_session,valid_normal_user_1 ,valid_normal_user_2, mock_post_1):
    """Test unverified user trying to list comments without following the author"""

    user1 = Users(**valid_normal_user_2)
    db_session.add_all([user1])
    db_session.commit()

    with patch("apps.posts.domain.service.get_followers", return_value=[]):
        with pytest.raises(HTTPException) as exc:
            list_comments_instance(
                post_id=1,
                session=db_session,
                current_user=user1,
            )

        assert exc.value.status_code == 403
        assert exc.value.detail == "You must follow the post author to list comments."

