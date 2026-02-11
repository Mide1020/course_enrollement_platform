from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schema.course import CourseCreate, CourseUpdate, CourseResponse
from app.crud.course import course_crud
from app.api.deps import get_current_admin
from app.models.user import User
import uuid


router = APIRouter()

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN ONLY
):
    
    # Check if course code already exists
    existing_course = course_crud.get_by_code(db, code=course.code)
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )
    
    # Create the course
    db_course = course_crud.create(db, course=course)
    
    return db_course


    
# PUBLIC ENDPOINTS (No authentication required)

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    courses = course_crud.get_all_active(db, skip=skip, limit=limit)
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    
    course = course_crud.get_by_id(db, course_id=course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: uuid.UUID,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN ONLY
):
    
    # Check if course exists
    existing_course = course_crud.get_by_id(db, course_id=course_id)
    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # If updating code, check if new code already exists
    if course_update.code:
        code_exists = course_crud.get_by_code(db, code=course_update.code)
        if code_exists and code_exists.id != course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists"
            )
    
    # Update the course
    updated_course = course_crud.update(db, course_id=course_id, course_update=course_update)
    
    return updated_course


@router.delete("/{course_id}", response_model=CourseResponse)
def delete_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN ONLY
):
    course = course_crud.delete(db, course_id=course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.patch("/{course_id}/activate", response_model=CourseResponse)
def activate_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN ONLY
):
    
    course = course_crud.activate(db, course_id=course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course