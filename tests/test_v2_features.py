import pytest
from io import BytesIO
import uuid
from app.models.enrollment import Enrollment, EnrollmentStatus

def test_upload_file(client, instructor_token):
    # Create a dummy file
    file_content = b"This is a test syllabus file."
    file = BytesIO(file_content)
    
    response = client.post(
        "/api/v1/content/upload",
        headers={"Authorization": f"Bearer {instructor_token}"},
        files={"file": ("syllabus.pdf", file, "application/pdf")}
    )
    
    assert response.status_code == 201
    assert "url" in response.json()
    assert response.json()["url"].startswith("/uploads/")

def test_course_filtering(client, admin_token):
    # Create courses with different categories and difficulties
    client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Beginner Python", "code": "PY101", "capacity": 30, "category": "Programming", "difficulty_level": "Beginner"}
    )
    client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Advanced Java", "code": "JV201", "capacity": 20, "category": "Programming", "difficulty_level": "Advanced"}
    )
    client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Intermediate Design", "code": "DSGN102", "capacity": 25, "category": "Design", "difficulty_level": "Intermediate"}
    )
    
    # Filter by difficulty
    response = client.get("/api/v1/courses/?difficulty=Beginner")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "PY101"
    
    # Filter by category
    response = client.get("/api/v1/courses/?category=Design")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "DSGN102"

def test_instructor_dashboard(client, instructor_token, admin_token, db, test_instructor, test_student):
    # Create a course assigned to this instructor
    course_response = client.post(
        "/api/v1/courses/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Instructor Course", 
            "code": "INST101", 
            "capacity": 50, 
            "instructor_id": str(test_instructor.id)
        }
    )
    course_id = uuid.UUID(course_response.json()["id"])
    
    # Enroll a student
    enrollment = Enrollment(user_id=test_student.id, course_id=course_id, status=EnrollmentStatus.ENROLLED)
    db.add(enrollment)
    db.commit()
    
    # Get dashboard
    response = client.get(
        "/api/v1/analytics/instructor/dashboard",
        headers={"Authorization": f"Bearer {instructor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_active_students"] == 1
    assert data["course_breakdown"][0]["course_code"] == "INST101"
    assert data["course_breakdown"][0]["enrollment_count"] == 1
