import pytest
from app.models.user import User, UserRole
from app.models.course import Course
from app.core.security import get_password_hash
import uuid

def test_course_content_flow(client, db):
    # 1. Create an instructor
    instructor = User(
        email="instructor_content@test.com",
        name="Content Instructor",
        hashed_password=get_password_hash("password123"),
        role=UserRole.INSTRUCTOR,
        is_active=True
    )
    db.add(instructor)
    db.commit()
    db.refresh(instructor)

    # 2. Login as instructor
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "instructor_content@test.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create a course
    course = Course(
        title="Web Development", 
        code="WD101", 
        capacity=50, 
        instructor_id=instructor.id, 
        is_active=True,
        difficulty_level="Beginner"
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # 4. Create a module
    module_data = {
        "title": "HTML Basics",
        "order": 1,
        "course_id": str(course.id)
    }
    module_response = client.post("/api/v1/content/modules", json=module_data, headers=headers)
    assert module_response.status_code == 201
    module_id = module_response.json()["id"]

    # 5. Create a lesson
    lesson_data = {
        "title": "Introduction to Tags",
        "content_type": "text",
        "content_data": "HTML tags are the building blocks...",
        "order": 1,
        "module_id": module_id
    }
    lesson_response = client.post("/api/v1/content/lessons", json=lesson_data, headers=headers)
    assert lesson_response.status_code == 201
    lesson_id = lesson_response.json()["id"]

    # 6. Get course content as a student (or any logged in user)
    # Using the same token for simplicity here, but active user check is sufficient
    content_response = client.get(f"/api/v1/content/courses/{course.id}/modules", headers=headers)
    assert content_response.status_code == 200
    content = content_response.json()
    assert len(content) == 1
    assert content[0]["title"] == "HTML Basics"
    assert len(content[0]["lessons"]) == 1
    assert content[0]["lessons"][0]["title"] == "Introduction to Tags"

    # 7. Update a lesson
    update_data = {"title": "Intro to HTML Tags"}
    update_response = client.patch(f"/api/v1/content/lessons/{lesson_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Intro to HTML Tags"

    # 8. Delete a module (should delete lessons too)
    delete_response = client.delete(f"/api/v1/content/modules/{module_id}", headers=headers)
    assert delete_response.status_code == 204

    # 9. Verify deletion
    verify_response = client.get(f"/api/v1/content/courses/{course.id}/modules", headers=headers)
    assert len(verify_response.json()) == 0
