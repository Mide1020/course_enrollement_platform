from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
import shutil
import os
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.api import deps
from app.crud.module import module_crud
from app.crud.lesson import lesson_crud
from app.crud.course import course_crud
from app.crud.enrollment import enrollment_crud
from app.schema.module import ModuleCreate, ModuleUpdate, ModuleResponse, ModuleWithLessons
from app.schema.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.models.user import User, UserRole

router = APIRouter()


# --- Module Endpoints ---

@router.post("/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Create a new module for a course. Instructor only."""
    course = course_crud.get_by_id(db, course_id=module.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can add modules")
    
    db_module = module_crud.create(db, module=module)
    db.commit()
    db.refresh(db_module)
    return db_module


@router.get("/courses/{course_id}/modules", response_model=List[ModuleWithLessons])
def get_course_modules(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get all modules for a course with their lessons.
    Instructors and admins can view any course.
    Students must be enrolled in the course.
    """
    # Enrollment gate: students must be enrolled
    if current_user.role == UserRole.STUDENT:
        enrollment = enrollment_crud.get_by_user_and_course(
            db, user_id=current_user.id, course_id=course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to view its content"
            )
    return module_crud.get_by_course(db, course_id=course_id)


@router.patch("/modules/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: uuid.UUID,
    module_update: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Update a module. Instructor only."""
    db_module = module_crud.get_by_id(db, module_id=module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Check if user is the instructor of the course
    course = course_crud.get_by_id(db, course_id=db_module.course_id)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can update modules")
    
    updated_module = module_crud.update(db, module_id=module_id, module_update=module_update)
    db.commit()
    db.refresh(updated_module)
    return updated_module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Delete a module. Instructor only."""
    db_module = module_crud.get_by_id(db, module_id=module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    course = course_crud.get_by_id(db, course_id=db_module.course_id)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can delete modules")
    
    module_crud.delete(db, module_id=module_id)
    db.commit()
    return None


# --- Lesson Endpoints ---

@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Create a new lesson for a module. Instructor only."""
    module = module_crud.get_by_id(db, module_id=lesson.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    course = course_crud.get_by_id(db, course_id=module.course_id)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can add lessons")
    
    db_lesson = lesson_crud.create(db, lesson=lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get a specific lesson."""
    db_lesson = lesson_crud.get_by_id(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return db_lesson


@router.patch("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: uuid.UUID,
    lesson_update: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Update a lesson. Instructor only."""
    db_lesson = lesson_crud.get_by_id(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    module = module_crud.get_by_id(db, module_id=db_lesson.module_id)
    course = course_crud.get_by_id(db, course_id=module.course_id)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can update lessons")
    
    updated_lesson = lesson_crud.update(db, lesson_id=lesson_id, lesson_update=lesson_update)
    db.commit()
    db.refresh(updated_lesson)
    return updated_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """Delete a lesson. Instructor only."""
    db_lesson = lesson_crud.get_by_id(db, lesson_id=lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    module = module_crud.get_by_id(db, module_id=db_lesson.module_id)
    course = course_crud.get_by_id(db, course_id=module.course_id)
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the course instructor can delete lessons")
    
    lesson_crud.delete(db, lesson_id=lesson_id)
    db.commit()
    return None


# --- File Upload Endpoint ---

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_instructor)
):
    """
    Upload a file (syllabus or lesson resource).
    Returns the URL to access the file.
    Instructor only.
    """
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create a unique filename to avoid collisions
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return the relative URL
    return {"url": f"/uploads/{unique_filename}"}
