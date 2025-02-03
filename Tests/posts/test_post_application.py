# def test_create_post_application(mock_session, mock_user):
#     result = create_post_application(mock_session, "Sample Title", "Sample Content", mock_user, None)
#     assert result is not None


# def test_create_post_application_missing_title(mock_session, mock_user):
#     with pytest.raises(ValueError):  # Assuming validation exists
#         create_post_application(mock_session, "", "Sample Content", mock_user, None)


# ### 2. List Posts ###
# def test_list_posts_application(mock_session, mock_user):
#     result = list_posts_application(mock_session, mock_user, skip=0, limit=10)
#     assert isinstance(result, list)


# def test_list_posts_application_invalid_limit(mock_session, mock_user):
#     with pytest.raises(ValueError):  # Assuming validation exists
#         list_posts_application(mock_session, mock_user, skip=0, limit=-5)


# ### 3. List Recommended Posts ###
# def test_list_recommended_posts_application(mock_session, mock_user):
#     result = list_recommended_posts_application(mock_session, mock_user)
#     assert isinstance(result, list)


# ### 4. Update Post ###
# def test_update_post_application(mock_session, mock_user, mock_post):
#     result = update_post_application(mock_post["id"], mock_session, mock_user, title="Updated Title")
#     assert result is not None


# def test_update_post_application_not_found(mock_session, mock_user):
#     with pytest.raises(ValueError):  # Assuming exception for non-existing post
#         update_post_application(99999, mock_session, mock_user, title="Updated Title")


# ### 5. Delete Post ###
# def test_delete_post_application(mock_session, mock_user, mock_post):
#     result = delete_post_application(mock_post["id"], mock_session, mock_user)
#     assert result is not None


# def test_delete_post_application_not_found(mock_session, mock_user):
#     with pytest.raises(ValueError):
#         delete_post_application(99999, mock_session, mock_user)


# ### 6. Report Post ###
# def test_report_post_application(mock_session, mock_user, mock_post):
#     result = report_post_application(mock_post["id"], mock_session, mock_user)
#     assert result is not None


# def test_report_post_application_not_found(mock_session, mock_user):
#     with pytest.raises(ValueError):
#         report_post_application(99999, mock_session, mock_user)


# ### 7. Create Comment ###
# def test_create_comment_application(mock_session, mock_user, mock_post):
#     result = create_comment_application(mock_post["id"], "Test Comment", mock_session, mock_user)
#     assert result is not None


# def test_create_comment_application_missing_content(mock_session, mock_user, mock_post):
#     with pytest.raises(ValueError):
#         create_comment_application(mock_post["id"], "", mock_session, mock_user)


# ### 8. List Comments ###
# def test_list_comments_application(mock_session, mock_user, mock_post):
#     result = list_comments_application(mock_post["id"], mock_session, mock_user)
#     assert isinstance(result, list)


# def test_list_comments_application_invalid_post_id(mock_session, mock_user):
#     with pytest.raises(ValueError):
#         list_comments_application(99999, mock_session, mock_user)


# ### 9. Update Comment ###
# def test_update_comment_application(mock_session, mock_user, mock_post, mock_comment):
#     result = update_comment_application(mock_post["id"], "Updated Comment", mock_comment["id"], mock_session, mock_user)
#     assert result is not None


# def test_update_comment_application_not_found(mock_session, mock_user, mock_post):
#     with pytest.raises(ValueError):
#         update_comment_application(mock_post["id"], "Updated Comment", 99999, mock_session, mock_user)


# ### 10. Delete Comment ###
# def test_delete_comment_application(mock_session, mock_user, mock_post, mock_comment):
#     result = delete_comment_application(mock_post["id"], mock_comment["id"], mock_session, mock_user)
#     assert result is not None


# def test_delete_comment_application_not_found(mock_session, mock_user, mock_post):
#     with pytest.raises(ValueError):
#         delete_comment_application(mock_post["id"], 99999, mock_session, mock_user)


# ### 11. Create Like ###
# def test_create_like_application(mock_session, mock_user, mock_post):
#     result = create_like_application(mock_post["id"], mock_session, mock_user)
#     assert result is not None


# def test_create_like_application_invalid_post(mock_session, mock_user):
#     with pytest.raises(ValueError):
#         create_like_application(99999, mock_session, mock_user)
