from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
import uuid


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    # Admins cannot self-register; admin accounts must be created by other admins directly in DB
    role: str = Field(default="student", pattern="^(student|instructor)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: uuid.UUID
    role: str
    is_active: bool
    bio: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)  # Allows converting SQLAlchemy model to Pydantic


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    """Schema for users updating their own profile."""
    name: Optional[str] = None
    bio: Optional[str] = None