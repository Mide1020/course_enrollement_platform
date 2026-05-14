from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schema.review import ReviewCreate, ReviewResponse
from app.crud.review import review_crud
from app.crud.enrollment import enrollment_crud
from app.api.deps import get_current_student
from app.models.user import User
from app.models.enrollment import EnrollmentStatus
import uuid


router = APIRouter()


@router.post("/{course_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    course_id: uuid.UUID,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    # Check if student has completed the course
    enrollment = enrollment_crud.get_by_user_and_course(db, user_id=current_user.id, course_id=course_id)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be enrolled in the course to leave a review"
        )
    
    if enrollment.status != EnrollmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review courses you have completed"
        )
    
    # Check if review already exists
    if enrollment.review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this course"
        )

    db_review = review_crud.create(
        db, 
        user_id=current_user.id, 
        course_id=course_id, 
        enrollment_id=enrollment.id, 
        review=review
    )
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/{course_id}", response_model=List[ReviewResponse])
def get_course_reviews(
    course_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return review_crud.get_by_course(db, course_id=course_id, skip=skip, limit=limit)
