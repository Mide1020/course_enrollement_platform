from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid
from app.schema.user import UserResponse
from app.schema.course import CourseResponse
from app.models.enrollment import EnrollmentStatus


class EnrollmentBase(BaseModel):
    course_id: uuid.UUID


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatus] = None
    grade: Optional[str] = None


class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    status: EnrollmentStatus
    grade: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithDetails(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    status: EnrollmentStatus
    grade: Optional[str] = None
    created_at: datetime
    user: UserResponse
    course: CourseResponse
    
    model_config = ConfigDict(from_attributes=True)