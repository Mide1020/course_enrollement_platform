from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
import uuid


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    code: str
    capacity: int = Field(..., gt=0)
    category: Optional[str] = None
    difficulty_level: Optional[str] = "Beginner"
    syllabus_url: Optional[str] = None


class CourseCreate(CourseBase):
    instructor_id: Optional[uuid.UUID] = None
    prerequisite_ids: Optional[List[uuid.UUID]] = []


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    category: Optional[str] = None
    instructor_id: Optional[uuid.UUID] = None
    syllabus_url: Optional[str] = None
    prerequisite_ids: Optional[List[uuid.UUID]] = None


class CourseResponse(CourseBase):
    id: uuid.UUID
    is_active: bool
    instructor_id: Optional[uuid.UUID] = None
    enrollment_count: int = 0
    waitlist_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class CourseWithDetails(CourseResponse):
    prerequisites: List[CourseResponse] = []
    
    model_config = ConfigDict(from_attributes=True)