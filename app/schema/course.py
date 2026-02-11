from pydantic import BaseModel, Field
from typing import Optional
import uuid


class CourseBase(BaseModel):
    title: str
    code: str
    capacity: int = Field(..., gt=0)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class CourseResponse(CourseBase):
    id: uuid.UUID
    is_active: bool
    
    class Config:
        from_attributes = True