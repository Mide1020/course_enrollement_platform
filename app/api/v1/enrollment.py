from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schema.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails
from app.crud.enrollment import enrollment_crud
from app.crud.course import course_crud
from app.api.deps import get_current_student, get_current_admin, get_current_active_user
from app.models.user import User
import uuid


router = APIRouter()


# STUDENT ENROLLMENT ENDPOINTS

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    
    # Check if the  course exists
    course = course_crud.get_by_id(db, course_id=enrollment.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Business Rule: Student cannot enroll if the course is inactive
    if not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot enroll in inactive course"
        )
    
    # Business Rule: Student cannot enroll in the  same course twice
    existing_enrollment = enrollment_crud.get_by_user_and_course(
        db, 
        user_id=current_user.id, 
        course_id=enrollment.course_id
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Business Rule: (Cannot enroll if course is full)
    enrollment_count = enrollment_crud.count_enrollments_for_course(
        db, 
        course_id=enrollment.course_id
    )
    if enrollment_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full"
        )
    
    # All checks passed - create enrollment
    db_enrollment = enrollment_crud.create(
        db, 
        enrollment=enrollment, 
        user_id=current_user.id
    )
    
    return db_enrollment


@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def deregister_from_course(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)  # STUDENT ONLY
):
    # Check if enrollment exists
    enrollment = enrollment_crud.get_by_id(db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check if enrollment belongs to current user
    if enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deregister from another student's enrollment"
        )
    
    # Delete enrollment
    deleted_enrollment = enrollment_crud.delete(db, enrollment_id=enrollment_id)
    
    return deleted_enrollment


# ADMIN ENDPOINTS

@router.get("/", response_model=List[EnrollmentWithDetails])
def get_all_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN ONLY
):
    enrollments = enrollment_crud.get_all(db, skip=skip, limit=limit)
    return enrollments


@router.get("/course/{course_id}", response_model=List[EnrollmentWithDetails])
def get_course_enrollments(
    course_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    
    # Check if the course already exists
    course = course_crud.get_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    enrollments = enrollment_crud.get_by_course(db, course_id=course_id, skip=skip, limit=limit)
    return enrollments

# ADMIN ONLY
@router.delete("/admin/{enrollment_id}", response_model=EnrollmentResponse)
def admin_remove_enrollment(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    enrollment = enrollment_crud.delete(db, enrollment_id=enrollment_id)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    return enrollment