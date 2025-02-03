from unittest.mock import MagicMock, patch
from apps.user.application.schemas import BaseResponse

@patch("apps.posts.application.service.create_post_instance")
def test_create_post(client,mock_create_post_instance):
    mock_create_post_instance.return_value = BaseResponse(success=True,data={"title": "Test Post", "content": "This is a test post"},message="Post created successfully!")
    response = client.post("/", json={"title": "Test Post", "content": "This is a test post"})
    assert response.status_code == 200
    assert response.json()["success"] is True

# @patch("apps.posts.application.service.create_post_instance")
# def test_create_post_missing_title(client,mock_create_post_instance):
#     mock_create_post_instance.return_value = BaseResponse(success=True,data={"title": "Test Post", "content": "This is a test post"},message="Post created successfully!")
#     response = client.post("/", json={"content": "Missing title"})
#     assert response.status_code == 400

# def test_create_post_unauthenticated(client):
#     app.dependency_overrides[get_current_user] = lambda: None  
#     response = client.post("/", json={"title": "Test Post", "content": "Test"})
#     assert response.status_code == 401
#     app.dependency_overrides[get_current_user] = mock_get_current_user  

# def test_list_posts(client):
#     response = client.get("/")
#     assert response.status_code == 200
#     assert isinstance(response.json()["data"], list)

# def test_list_posts_unauthenticated(client):
#     app.dependency_overrides[get_current_user] = lambda: None
#     response = client.get("/")
#     assert response.status_code == 401
#     app.dependency_overrides[get_current_user] = mock_get_current_user

# def test_update_post(client,test_post):
#     response = client.put(f"/{test_post}/", json={"title": "Updated Post"})
#     assert response.status_code == 200
#     assert response.json()["data"]["title"] == "Updated Post"

# def test_update_post_not_found(client):
#     response = client.put("/99999/", json={"title": "Non-existent post"})
#     assert response.status_code == 404

# def test_delete_post(client,test_post):
#     response = client.delete(f"/{test_post}/")
#     assert response.status_code == 200

# def test_delete_post_unauthorized(client):
#     app.dependency_overrides[get_current_user] = lambda: {"id": 2, "username": "otheruser"}
#     response = client.delete("/1/")
#     assert response.status_code == 403
#     app.dependency_overrides[get_current_user] = mock_get_current_user

# def test_report_post(client,test_post):
#     response = client.post(f"/{test_post}/report/")
#     assert response.status_code == 200

# def test_report_post_not_found(client):
#     response = client.post("/99999/report/")
#     assert response.status_code == 404

# def test_create_comment(client,test_post):
#     response = client.post(f"/{test_post}/comments/create/", json={"content": "Test comment"})
#     assert response.status_code == 200

# def test_create_comment_unauthenticated(client,):
#     app.dependency_overrides[get_current_user] = lambda: None
#     response = client.post("/1/comments/create/", json={"content": "Test comment"})
#     assert response.status_code == 401
#     app.dependency_overrides[get_current_user] = mock_get_current_user

# def test_list_comments(client,test_post):
#     response = client.get(f"/{test_post}/comments")
#     assert response.status_code == 200
#     assert isinstance(response.json()["data"], list)

# def test_list_comments_post_not_found(client,):
#     response = client.get("/99999/comments")
#     assert response.status_code == 404

# def test_update_comment(client,test_post, test_comment):
#     response = client.put(f"/{test_post}/comments/{test_comment}/", json={"content": "Updated comment"})
#     assert response.status_code == 200

# def test_update_comment_not_found(client,test_post):
#     response = client.put(f"/{test_post}/comments/99999/", json={"content": "Updated comment"})
#     assert response.status_code == 404

# def test_delete_comment(client,test_post, test_comment):
#     response = client.delete(f"/{test_post}/comments/{test_comment}/delete/")
#     assert response.status_code == 200

# def test_delete_comment_not_found(client,test_post):
#     response = client.delete(f"/{test_post}/comments/99999/delete/")
#     assert response.status_code == 404

# def test_like_post(client,test_post):
#     response = client.post(f"/{test_post}/like")
#     assert response.status_code == 200

# def test_like_post_not_found(client,):
#     response = client.post("/99999/like")
#     assert response.status_code == 404