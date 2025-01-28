test_user_data = {
    "username": "viveksoniii",
    "name": "viveksoni",
    "first_name": "vivesonoi",
    "last_name": "strsdsdving",
    "email": "user@example.com",
    "password": "13November200@",
}


def test_register_user(client):
    response = client.post("/auth/register", json=test_user_data)
    print("Response status:", response.status_code)
    print("Response body:", response.json())
    assert response.status_code == 200
    response_json = response.json()
    assert "username" in response_json
    assert response_json["username"] == test_user_data["username"]
    assert response_json["email"] == test_user_data["email"]
