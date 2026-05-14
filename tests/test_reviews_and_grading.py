import pytest
from app.models.enrollment import EnrollmentStatus
from app.models.course import Course
import uuid

def test_grading_enrollment(client, instructor_token, test_instructor, test_student, db):
    # Create a course with the instructor
    course = Course(
        title="Graded Course",
        code="GRAD101",
        capacity=30,
        instructor_id=test_instructor.id
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Enroll student (direct DB for speed in test)
    from app.models.enrollment import Enrollment
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    # Grade student
    response = client.patch(
        f"/api/v1/enrollments/{enrollment.id}/grade",
        headers={"Authorization": f"Bearer {instructor_token}"},
        json={"status": "completed", "grade": "A"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["grade"] == "A"
    
    # Check transcript
    student_token_response = client.post(
        "/api/v1/auth/login",
        data={"username": test_student.email, "password": "password123"}
    )
    student_token = student_token_response.json()["access_token"]
    
    transcript_response = client.get(
        "/api/v1/enrollments/me/transcript",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert transcript_response.status_code == 200
    transcript_data = transcript_response.json()
    assert len(transcript_data) == 1
    assert transcript_data[0]["grade"] == "A"


def test_review_course(client, test_student, test_instructor, db):
    # Login student
    student_token_response = client.post(
        "/api/v1/auth/login",
        data={"username": test_student.email, "password": "password123"}
    )
    student_token = student_token_response.json()["access_token"]
    
    # Create course and completed enrollment
    course = Course(title="Reviewable Course", code="REV101", capacity=30)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    from app.models.enrollment import Enrollment
    enrollment = Enrollment(
        user_id=test_student.id, 
        course_id=course.id, 
        status=EnrollmentStatus.COMPLETED,
        grade="B"
    )
    db.add(enrollment)
    db.commit()
    
    # Post review
    response = client.post(
        f"/api/v1/reviews/{course.id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"rating": 5, "comment": "Excellent course!"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Excellent course!"
    
    # Get reviews
    get_response = client.get(f"/api/v1/reviews/{course.id}")
    assert get_response.status_code == 200
    reviews = get_response.json()
    assert len(reviews) == 1
    assert reviews[0]["comment"] == "Excellent course!"


def test_review_uncompleted_course_fails(client, test_student, db):
    # Login student
    student_token_response = client.post(
        "/api/v1/auth/login",
        data={"username": test_student.email, "password": "password123"}
    )
    student_token = student_token_response.json()["access_token"]
    
    # Create course and active enrollment (not completed)
    course = Course(title="Ongoing Course", code="ONG101", capacity=30)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    from app.models.enrollment import Enrollment
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id, status=EnrollmentStatus.ENROLLED)
    db.add(enrollment)
    db.commit()
    
    # Try to post review
    response = client.post(
        f"/api/v1/reviews/{course.id}",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"rating": 4, "comment": "Good so far"}
    )
    
    assert response.status_code == 400
    assert "only review courses you have completed" in response.json()["detail"]
