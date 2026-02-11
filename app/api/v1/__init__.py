from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as users_router
from app.api.v1.courses import router as courses_router
from app.api.v1.enrollment import router as enrollment_router

api_router = APIRouter()


api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

api_router.include_router(users_router, prefix="/users", tags=["Users"])

api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])

api_router.include_router(enrollment_router, prefix="/enrollments", tags=["Enrollments"])