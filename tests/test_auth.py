def test_register_student(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newstudent@test.com",
            "name": "New Student",
            "password": "password123",
            "role": "student"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "newstudent@test.com"
    assert data["name"] == "New Student"
    assert data["role"] == "student"
    assert "password" not in data


def test_register_duplicate_email(client, test_student):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teststudent@test.com",
            "name": "Another Student",
            "password": "password123",
            "role": "student"
        }
    )

    assert response.status_code in (400, 409)
    assert "already" in response.json()["detail"].lower()


def test_login_success(client, test_student):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "teststudent@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_student):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "teststudent@test.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401


def test_login_inactive_user(client, db, test_student):
    test_student.is_active = False
    db.commit()
    db.refresh(test_student)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "teststudent@test.com",
            "password": "password123"
        }
    )

    assert response.status_code in (401, 403)
