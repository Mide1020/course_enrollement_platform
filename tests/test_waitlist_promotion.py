import pytest
import uuid
from app.models.enrollment import Enrollment, EnrollmentStatus

def test_waitlist_promotion_notification(client, admin_token, student_token, test_student, test_instructor, db):
    # 1. Create a course with capacity 1
    course_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Small Course", 
            "code": "SMALL101", 
            "capacity": 1, 
            "instructor_id": str(test_instructor.id)
        }
    )
    course_id = course_response.json()["id"]
    
    # 2. Enroll first student (manually so we don't need another token)
    other_student_id = uuid.uuid4()
    # (Actually it's better to use another real student if possible, but let's just use the current student for now)
    # Let's enroll the 'test_student' first.
    client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": course_id}
    )
    
    # 3. Join waitlist with another student
    # I'll create a second student
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    second_student = User(
        email="second@test.com",
        name="Second Student",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(second_student)
    db.commit()
    
    second_token_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "second@test.com", "password": "password123"}
    )
    second_token = second_token_resp.json()["access_token"]
    
    # Join waitlist
    client.post(
        "/api/v1/waitlist/",
        headers={"Authorization": f"Bearer {second_token}"},
        json={"course_id": course_id}
    )
    
    # 4. Deregister first student
    # Get enrollment id
    enrollments_resp = client.get(
        "/api/v1/enrollments/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    enrollment_id = enrollments_resp.json()[0]["id"]
    
    # Deregister - this should trigger promotion
    response = client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 200
    
    # 5. Verify second student is now enrolled
    second_enrollments = client.get(
        "/api/v1/enrollments/me",
        headers={"Authorization": f"Bearer {second_token}"}
    )
    assert len(second_enrollments.json()) == 1
    assert second_enrollments.json()[0]["course_id"] == course_id
    assert second_enrollments.json()[0]["status"] == "enrolled"
