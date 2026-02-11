from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
from app.schema.user import UserResponse
from app.schema.course import CourseResponse


class EnrollmentBase(BaseModel):
    course_id: uuid.UUID


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnrollmentWithDetails(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    user: UserResponse
    course: CourseResponse
    
    class Config:
        from_attributes = True