from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import uuid


class ModuleBase(BaseModel):
    title: str
    order: int = 0


class ModuleCreate(ModuleBase):
    course_id: uuid.UUID


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None


class ModuleResponse(ModuleBase):
    id: uuid.UUID
    course_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class ModuleWithLessons(ModuleResponse):
    lessons: List["LessonResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)

from app.schema.lesson import LessonResponse
