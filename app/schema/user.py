from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = Field(default="student", pattern="^(student|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to Pydantic


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None