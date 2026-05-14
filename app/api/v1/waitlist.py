from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schema.waitlist import WaitlistCreate, WaitlistResponse
from app.crud.waitlist import waitlist_crud
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.api.deps import get_current_student, get_current_admin
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def join_waitlist(
    waitlist_in: WaitlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    course = course_crud.get_by_id(db, course_id=waitlist_in.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # Check if already enrolled
    existing_enrollment = enrollment_crud.get_by_user_and_course(db, user_id=current_user.id, course_id=waitlist_in.course_id)
    if existing_enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled in this course")
    
    # Check if already on waitlist
    # Check if already on waitlist
    existing_waitlist = waitlist_crud.get_by_user_and_course(db, user_id=current_user.id, course_id=waitlist_in.course_id)
    if existing_waitlist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already on waitlist for this course")
    
    # Create waitlist entry
    db_entry = waitlist_crud.create(db, user_id=current_user.id, course_id=waitlist_in.course_id)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_waitlist(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student)
):
    success = waitlist_crud.remove_user_from_course_waitlist(db, user_id=current_user.id, course_id=course_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waitlist entry not found")
    
    db.commit()
    return None


@router.get("/course/{course_id}", response_model=List[WaitlistResponse])
def get_course_waitlist(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return waitlist_crud.get_by_course(db, course_id=course_id)
