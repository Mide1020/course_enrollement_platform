import pytest
from app.models.user import User, UserRole
from app.models.course import Course
from app.core.security import get_password_hash

def test_course_search_and_filter(client, db):
    # Create courses in different categories
    c1 = Course(title="Python Basics", code="PY101", capacity=30, category="Programming", is_active=True)
    c2 = Course(title="Advanced Python", code="PY201", capacity=20, category="Programming", is_active=True)
    c3 = Course(title="Introduction to Art", code="ART101", capacity=15, category="Arts", is_active=True)
    db.add_all([c1, c2, c3])
    db.commit()

    # Search by title
    response = client.get("/api/v1/courses/?search=Basics")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Basics"

    # Filter by category
    response = client.get("/api/v1/courses/?category=Arts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Introduction to Art"

def test_instructor_role(client, db):
    # Create instructor
    instructor = User(
        email="teacher@test.com",
        name="Teacher",
        hashed_password=get_password_hash("password123"),
        role=UserRole.INSTRUCTOR,
        is_active=True
    )
    db.add(instructor)
    db.commit()
    db.refresh(instructor)

    # Login as instructor
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "teacher@test.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Create course with this instructor
    course = Course(title="Teaching 101", code="TE101", capacity=10, instructor_id=instructor.id, is_active=True)
    db.add(course)
    db.commit()

    # Check my-courses
    response = client.get(
        "/api/v1/courses/instructor/my-courses",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "TE101"

def test_prerequisites_enforcement(client, student_token, db, test_student):
    # Create courses
    intro = Course(title="Intro", code="CS101", capacity=50, is_active=True)
    db.add(intro)
    db.commit()
    db.refresh(intro)

    advanced = Course(title="Advanced", code="CS201", capacity=50, is_active=True)
    advanced.prerequisites = [intro]
    db.add(advanced)
    db.commit()
    db.refresh(advanced)

    # Try to enroll in Advanced without Intro
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(advanced.id)}
    )
    assert response.status_code == 400
    assert "Prerequisite not met" in response.json()["detail"]

    # Enroll in Intro first
    client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(intro.id)}
    )

    # Now try Advanced again
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(advanced.id)}
    )
    assert response.status_code == 201

def test_waitlist_system(client, student_token, db, test_student):
    # Create course with capacity 1
    course = Course(title="Full Course", code="FULL101", capacity=1, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)

    # Enroll another user to fill the course
    other_user = User(
        email="other_student@test.com",
        name="Other Student",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    from app.models.enrollment import Enrollment
    db.add(Enrollment(user_id=other_user.id, course_id=course.id))
    db.commit()

    # Try to enroll (should fail)
    enroll_response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    assert enroll_response.status_code == 400
    assert "full" in enroll_response.json()["detail"].lower()

    # Join waitlist
    waitlist_response = client.post(
        "/api/v1/waitlist/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    assert waitlist_response.status_code == 201
    assert waitlist_response.json()["course_id"] == str(course.id)

    # Check course details (should show waitlist count)
    course_details = client.get(f"/api/v1/courses/{course.id}")
    assert course_details.status_code == 200
    assert course_details.json()["waitlist_count"] == 1
