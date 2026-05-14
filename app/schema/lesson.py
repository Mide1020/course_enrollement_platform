from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid


class LessonBase(BaseModel):
    title: str
    content_type: str
    content_data: Optional[str] = None
    order: int = 0
    resource_url: Optional[str] = None


class LessonCreate(LessonBase):
    module_id: uuid.UUID


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content_type: Optional[str] = None
    content_data: Optional[str] = None
    order: Optional[int] = None
    resource_url: Optional[str] = None


class LessonResponse(LessonBase):
    id: uuid.UUID
    module_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
