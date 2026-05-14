from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid


class WaitlistBase(BaseModel):
    course_id: uuid.UUID


class WaitlistCreate(WaitlistBase):
    pass


class WaitlistResponse(WaitlistBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
