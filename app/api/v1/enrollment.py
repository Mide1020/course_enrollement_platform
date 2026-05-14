from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schema.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails, EnrollmentUpdate
from app.crud.enrollment import enrollment_crud
from app.crud.course import course_crud
from app.crud.waitlist import waitlist_crud
from app.api.deps import get_current_student, get_current_admin, get_current_instructor
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.core.notifier import send_enrollment_notification, send_waitlist_promotion_notification
import uuid
import logging

logger = logging.getLogger("app")
router = APIRouter()


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Use a transaction for atomic enrollment
    try:
        # Fetch course with lock to prevent capacity race conditions
        course = db.query(Course).filter(Course.id == enrollment.course_id).with_for_update().first()
        
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
        if not course.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot enroll in inactive course")
        
        # Check prerequisites
        if course.prerequisites:
            student_enrollments = enrollment_crud.get_by_user(db, user_id=current_user.id)
            enrolled_course_ids = {e.course_id for e in student_enrollments}
            for prereq in course.prerequisites:
                if prereq.id not in enrolled_course_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"Prerequisite not met: {prereq.title} ({prereq.code})"
                    )

        # Check if already enrolled
        existing_enrollment = enrollment_crud.get_by_user_and_course(db, user_id=current_user.id, course_id=enrollment.course_id)
        if existing_enrollment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled in this course")
        
        # Check capacity
        enrollment_count = enrollment_crud.count_enrollments_for_course(db, course_id=enrollment.course_id)
        if enrollment_count >= course.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Course is full. Please join the waitlist."
            )
        
        # Create enrollment
        db_enrollment = enrollment_crud.create(db, course_id=enrollment.course_id, user_id=current_user.id)
        
        # If student was on waitlist, remove them
        waitlist_crud.remove_user_from_course_waitlist(db, user_id=current_user.id, course_id=enrollment.course_id)

        db.commit()
        db.refresh(db_enrollment)
        
        # Background notification after successful commit
        background_tasks.add_task(
            send_enrollment_notification, 
            user_email=current_user.email, 
            course_title=course.title
        )
        
        return db_enrollment
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during enrollment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during enrollment"
        )


@router.get("/me", response_model=List[EnrollmentWithDetails])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    return enrollment_crud.get_by_user(db, user_id=current_user.id)


@router.get("/me/transcript", response_model=List[EnrollmentWithDetails])
def get_my_transcript(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    enrollments = enrollment_crud.get_by_user(db, user_id=current_user.id)
    return [e for e in enrollments if e.status == EnrollmentStatus.COMPLETED]


@router.get("/me/waitlist")
def get_my_waitlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    """Get all waitlist entries for the current student."""
    from app.models.waitlist import WaitlistEntry
    from app.schema.waitlist import WaitlistResponse
    entries = db.query(WaitlistEntry).filter(WaitlistEntry.user_id == current_user.id).all()
    return entries


@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def deregister_from_course(
    enrollment_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    enrollment = enrollment_crud.get_by_id(db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    if enrollment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    course_id = enrollment.course_id
    
    # Use a transaction for atomic deregistration and promotion
    try:
        # Lock course to prevent capacity race conditions during promotion
        course = db.query(Course).filter(Course.id == course_id).with_for_update().first()
        
        # Delete current enrollment using CRUD method
        enrollment_crud.delete(db, enrollment_id=enrollment_id)
        
        # Check waitlist for promotion
        waitlist_entries = waitlist_crud.get_by_course(db, course_id=course_id)
        if waitlist_entries:
            next_entry = waitlist_entries[0]
            # Create new enrollment for the next person
            new_enrollment = Enrollment(user_id=next_entry.user_id, course_id=course_id)
            db.add(new_enrollment)
            # Remove from waitlist
            waitlist_crud.delete(db, entry_id=next_entry.id)
            
            # Send promotion notification in background
            background_tasks.add_task(
                send_waitlist_promotion_notification,
                user_email=next_entry.user.email,
                course_title=course.title
            )
            logger.info(f"Automatically promoted user {next_entry.user.email} to course {course.title}")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during deregistration/promotion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during deregistration"
        )
        
    return enrollment


@router.patch("/{enrollment_id}/grade", response_model=EnrollmentResponse)
def grade_student(
    enrollment_id: uuid.UUID,
    update_data: EnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    enrollment = enrollment_crud.get_by_id(db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    # Verify instructor owns the course
    course = course_crud.get_by_id(db, course_id=enrollment.course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    updated_enrollment = enrollment_crud.update(db, enrollment_id=enrollment_id, obj_in=update_data)
    db.commit()
    db.refresh(updated_enrollment)
    return updated_enrollment


# ADMIN ENDPOINTS

@router.get("/", response_model=List[EnrollmentWithDetails])
def get_all_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return enrollment_crud.get_all(db, skip=skip, limit=limit)


@router.get("/course/{course_id}/all", response_model=List[EnrollmentWithDetails])
def get_course_enrollments(
    course_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    """Get all enrollments for a specific course (Instructor or Admin)"""
    course = course_crud.get_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Allow if Admin OR the course instructor
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return enrollment_crud.get_by_course(db, course_id=course_id, skip=skip, limit=limit)


@router.delete("/admin/{enrollment_id}", response_model=EnrollmentResponse)
def admin_remove_enrollment(
    enrollment_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    enrollment = enrollment_crud.get_by_id(db, enrollment_id=enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    course_id = enrollment.course_id
    
    try:
        # Lock course
        course = db.query(Course).filter(Course.id == course_id).with_for_update().first()
        
        # Delete enrollment using CRUD
        enrollment_crud.delete(db, enrollment_id=enrollment_id)
        
        # Check waitlist for promotion
        waitlist_entries = waitlist_crud.get_by_course(db, course_id=course_id)
        if waitlist_entries:
            next_entry = waitlist_entries[0]
            new_enrollment = Enrollment(user_id=next_entry.user_id, course_id=course_id)
            db.add(new_enrollment)
            waitlist_crud.delete(db, entry_id=next_entry.id)
            
            background_tasks.add_task(
                send_waitlist_promotion_notification,
                user_email=next_entry.user.email,
                course_title=course.title
            )
            logger.info(f"Admin: Automatically promoted user {next_entry.user.email} to course {course.title}")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during admin deregistration/promotion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during deregistration"
        )
    
    return enrollment