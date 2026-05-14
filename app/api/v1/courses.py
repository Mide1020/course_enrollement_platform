from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schema.course import CourseCreate, CourseUpdate, CourseResponse, CourseWithDetails
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.crud.waitlist import waitlist_crud
from app.api.deps import get_current_admin, get_current_instructor, get_current_user
from app.models.user import User
import uuid


router = APIRouter()

def enrich_course(db: Session, course):
    if not course:
        return None
    course.enrollment_count = enrollment_crud.count_enrollments_for_course(db, course.id)
    course.waitlist_count = waitlist_crud.count_by_course(db, course.id)
    return course

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Admin or Instructor
):
    if current_user.role.value not in ["admin", "instructor"]:
        raise HTTPException(status_code=403, detail="Only instructors and admins can create courses")
    # Check if course code already exists
    existing_course = course_crud.get_by_code(db, code=course.code)
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )
    
    if course.instructor_id:
        instructor = db.query(User).filter(User.id == course.instructor_id).first()
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id {course.instructor_id} not found"
            )
    
    db_course = course_crud.create(db, course=course)
    db.commit()
    db.refresh(db_course)
    return enrich_course(db, db_course)


@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = Query(None, description="Search by title or code"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Beginner, Intermediate, Advanced)"),
    min_rating: Optional[float] = Query(None, description="Filter by minimum average rating"),
    db: Session = Depends(get_db)
):
    courses = course_crud.get_all_active(
        db, 
        skip=skip, 
        limit=limit, 
        search=search, 
        category=category,
        difficulty=difficulty,
        min_rating=min_rating
    )
    return [enrich_course(db, c) for c in courses]


# INSTRUCTOR ENDPOINTS — must be ABOVE /{course_id} to avoid route collision
@router.get("/instructor/my-courses", response_model=List[CourseResponse])
def get_instructor_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    courses = course_crud.get_by_instructor(db, instructor_id=current_user.id)
    return [enrich_course(db, c) for c in courses]


@router.get("/{course_id}", response_model=CourseWithDetails)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    course = course_crud.get_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return enrich_course(db, course)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: uuid.UUID,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    existing_course = course_crud.get_by_id(db, course_id=course_id)
    if not existing_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
    if current_user.role.value != "admin" and existing_course.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the course instructor or an admin can update this course")
    
    if course_update.code:
        code_exists = course_crud.get_by_code(db, code=course_update.code)
        if code_exists and code_exists.id != course_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")
    
    if course_update.instructor_id:
        instructor = db.query(User).filter(User.id == course_update.instructor_id).first()
        if not instructor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instructor with id {course_update.instructor_id} not found"
            )
    
    updated_course = course_crud.update(db, course_id=course_id, course_update=course_update)
    db.commit()
    db.refresh(updated_course)
    return enrich_course(db, updated_course)


@router.delete("/{course_id}", response_model=CourseResponse)
def delete_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_instructor)
):
    existing_course = course_crud.get_by_id(db, course_id=course_id)
    if not existing_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
    if current_user.role.value != "admin" and existing_course.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the course instructor or an admin can delete this course")

    course = course_crud.delete(db, course_id=course_id)
    
    db.commit()
    db.refresh(course)
    return enrich_course(db, course)

