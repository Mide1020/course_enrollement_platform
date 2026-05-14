from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
import uuid
from app.schema.user import UserResponse


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    enrollment_id: uuid.UUID
    created_at: datetime
    user: Optional[UserResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
