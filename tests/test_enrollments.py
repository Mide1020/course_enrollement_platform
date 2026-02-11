def test_student_enroll_in_course(client, student_token, db):
    from app.models.course import Course
    
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == str(course.id)


def test_student_enroll_duplicate(client, student_token, db, test_student):
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    
    # Create course
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Create existing enrollment
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    
    # Try to enroll again
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    
    assert response.status_code == 400
    assert "already enrolled" in response.json()["detail"].lower()


def test_student_enroll_in_full_course(client, student_token, db):
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # Create course with capacity 1
    course = Course(title="Limited Course", code="LM101", capacity=1, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Create another user and enroll them (fills the course)
    other_user = User(
        email="other@test.com",
        name="Other User",
        hashed_password=get_password_hash("password123"),
        role="student",
        is_active=True
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    enrollment = Enrollment(user_id=other_user.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    
    # Now course is full, try to enroll test student
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_student_enroll_in_inactive_course(client, student_token, db):
    from app.models.course import Course
    
    course = Course(title="Inactive Course", code="IN101", capacity=30, is_active=False)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.post(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"course_id": str(course.id)}
    )
    
    assert response.status_code == 400
    assert "inactive" in response.json()["detail"].lower()


def test_student_deregister_from_course(client, student_token, db, test_student):
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    
    # Create course
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Create enrollment
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    # Deregister
    response = client.delete(
        f"/api/v1/enrollments/{enrollment.id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 200


def test_admin_view_all_enrollments(client, admin_token, db, test_student):
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    
    # Create course
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Create enrollment using test_student fixture
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    
    response = client.get(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_student_cannot_view_all_enrollments(client, student_token):
    response = client.get(
        "/api/v1/enrollments/",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()


def test_admin_view_course_enrollments(client, admin_token, db):
    from app.models.course import Course
    
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    response = client.get(
        f"/api/v1/enrollments/course/{course.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200


def test_admin_remove_student_from_course(client, admin_token, db, test_student):
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    
    # Create course
    course = Course(title="Python 101", code="PY101", capacity=30, is_active=True)
    db.add(course)
    db.commit()
    db.refresh(course)
    
    # Create enrollment using test_student fixture
    enrollment = Enrollment(user_id=test_student.id, course_id=course.id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    # Admin removes enrollment
    response = client.delete(
        f"/api/v1/enrollments/admin/{enrollment.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200