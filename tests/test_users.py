def test_get_current_user_profile(client, student_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teststudent@test.com"
    assert data["name"] == "Test Student"
    assert data["role"] == "student"
    assert "password" not in data


def test_get_current_user_no_token(client):
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer fake-invalid-token"}
    )
    
    assert response.status_code == 401