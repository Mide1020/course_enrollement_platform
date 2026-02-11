from fastapi import APIRouter, Depends
from app.schema.user import UserResponse
from app.models.user import User
from app.api.deps import get_current_active_user


router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user