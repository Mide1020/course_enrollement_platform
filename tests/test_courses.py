def test_get_all_courses_public(client, db):
    # Create test courses directly in database
    from app.models.course import Course
    
    course1 = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    course2 = Course(title="Java 101", code="JV101", capacity=25, is_active=True)
    course3 = Course(title="Inactive Course", code="IN101", capacity=20, is_active=False)
    
    db.add_all([course1, course2, course3])
    db.commit()
    
    # No authentication required
    response = client.get("/api/v1/courses/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only active courses


def test_get_single_course(client, db):
    from app.models.course import Course
    
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.get(f"/api/v1/courses/{course.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python 101"
    assert data["code"] == "PY101"


def test_create_course_as_admin(client, admin_token):
    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Introduction to Python",
            "code": "CS101",
            "capacity": 30
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Introduction to Python"
    assert data["code"] == "CS101"
    assert data["capacity"] == 30
    assert data["is_active"] == True


def test_create_course_as_student(client, student_token):
    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "Unauthorized Course",
            "code": "CS999",
            "capacity": 10
        }
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


def test_create_course_duplicate_code(client, admin_token, db):
    from app.models.course import Course
    
    # Create existing course
    existing = Course(title="Existing", code="CS101", capacity=20, is_active=True)
    db.add(existing)
    db.commit()
    
    # Try to create with same code
    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "New Course",
            "code": "CS101",  # Duplicate!
            "capacity": 30
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_create_course_invalid_capacity(client, admin_token):
    response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Invalid Course",
            "code": "CS999",
            "capacity": 0  # Must be > 0
        }
    )
    
    assert response.status_code == 422


def test_update_course_as_admin(client, admin_token, db):
    from app.models.course import Course
    
    course = Course(title="Old Title", code="CS101", capacity=20, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.put(
        f"/api/v1/courses/{course.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Updated Title",
            "code": "CS101",
            "capacity": 25
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["capacity"] == 25


def test_update_course_as_student(client, student_token, db):
    from app.models.course import Course
    
    course = Course(title="Course", code="CS101", capacity=20, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.put(
        f"/api/v1/courses/{course.id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "title": "Hacked",
            "code": "CS101",
            "capacity": 999
        }
    )
    
    assert response.status_code == 403


def test_delete_course_as_admin(client, admin_token, db):
    from app.models.course import Course
    
    course = Course(title="Course", code="CS101", capacity=20, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.delete(
        f"/api/v1/courses/{course.id}/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False