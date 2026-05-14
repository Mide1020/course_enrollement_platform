from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schema.user import UserResponse, UserProfileUpdate
from app.models.user import User
from app.api.deps import get_current_active_user
from app.database import get_db


router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the current user's name and/or bio."""
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user