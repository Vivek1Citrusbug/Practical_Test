import pytest
from apps.posts.application.service import (
    create_comment_application,
    create_like_application,
    create_post_application,
    delete_comment_application,
    delete_post_application,
    list_comments_application,
    list_posts_application,
    report_post_application,
    update_comment_application,
    update_post_application,
)
from apps.posts.domain.models import Comments, Posts
from apps.user.domain.models import Connections, Users
from fastapi import HTTPException


def test_create_post_application(db_session, valid_normal_user_1):

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    result = create_post_application(
        db_session, "Sample Title", "Sample Content", user1, None
    )
    assert result is not None
    assert result.success == True


def test_list_posts_application(db_session, valid_normal_user_1):

    user1 = Users(**valid_normal_user_1)
    post1 = Posts(content="sample1", title="title1", post_by=user1.username)
    post2 = Posts(content="sample2", title="title2", post_by=user1.username)
    db_session.add_all([post1, post2])
    db_session.commit()

    result = list_posts_application(db_session, user1, skip=0, limit=10)
    assert result.success == True


def test_list_posts_application_invalid_limit(db_session, valid_normal_user_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException):
        list_posts_application(db_session, user1, skip=0, limit=-5)


def test_update_post_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    result = update_post_application(
        mock_post_1.id, db_session, user1, title="Updated Title"
    )
    assert result.success == True


def test_update_post_application_not_found(db_session, valid_normal_user_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    with pytest.raises(HTTPException):
        update_post_application(99999, db_session, user1, title="Updated Title")


def test_delete_post_application(db_session, valid_normal_user_1, mock_post_1):

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    result = delete_post_application(mock_post_1.id, db_session, user1)
    assert result.success == True


def test_delete_post_application_not_found(db_session, valid_normal_user_1):

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException):
        delete_post_application(99999, db_session, user1)


def test_report_post_application(db_session, valid_normal_user_2, mock_post_1):
    user1 = Users(**valid_normal_user_2)
    connection1 = Connections(
        follower=user1.username, following=mock_post_1.post_by, status=1
    )
    db_session.add_all([connection1, user1])
    db_session.commit()
    result = report_post_application(mock_post_1.id, db_session, user1)
    assert result.success == True


def test_report_post_application_not_found(db_session, valid_normal_user_2):
    user1 = Users(**valid_normal_user_2)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException):
        report_post_application(99999, db_session, user1)


def test_create_comment_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    result = create_comment_application(
        mock_post_1.id, "Test Comment", db_session, user1
    )
    assert result.success == True


def test_list_comments_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    comment = Comments(comment_by=user1.username, content="temp", post=mock_post_1.id)
    db_session.add_all([user1, comment])
    db_session.commit()
    result = list_comments_application(mock_post_1.id, db_session, user1)
    assert result.success == True


def test_list_comments_application_invalid_post_id(db_session, valid_normal_user_1):
    user1 = Users(**valid_normal_user_1)

    db_session.add(user1)
    db_session.commit()
    with pytest.raises(HTTPException):
        list_comments_application(99999, db_session, user1)


def test_update_comment_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    comment = Comments(comment_by=user1.username, content="temp", post=mock_post_1.id)
    db_session.add_all([user1, comment])
    db_session.commit()
    result = update_comment_application(
        mock_post_1.id, "Updated Comment", 1, db_session, user1
    )
    assert result.success == True


def test_update_comment_application_not_found(
    db_session, valid_normal_user_1, mock_post_1
):

    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(HTTPException):
        update_comment_application(
            mock_post_1.id, "Updated Comment", 99999, db_session, user1
        )


def test_delete_comment_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    comment = Comments(comment_by=user1.username, content="temp", post=mock_post_1.id)
    db_session.add_all([user1, comment])
    db_session.commit()
    result = delete_comment_application(mock_post_1.id, comment.id, db_session, user1)
    assert result.success == True


def test_delete_comment_application_not_found(
    db_session, valid_normal_user_1, mock_post_1
):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    with pytest.raises(HTTPException):
        delete_comment_application(mock_post_1.id, 99999, db_session, user1)


def test_create_like_application(db_session, valid_normal_user_1, mock_post_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    result = create_like_application(mock_post_1.id, db_session, user1)
    assert result is not None


def test_create_like_application_invalid_post(db_session, valid_normal_user_1):
    user1 = Users(**valid_normal_user_1)
    db_session.add(user1)
    db_session.commit()
    with pytest.raises(HTTPException):
        create_like_application(99999, db_session, user1)
