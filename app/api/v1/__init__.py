from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as users_router
from app.api.v1.courses import router as courses_router
from app.api.v1.enrollment import router as enrollment_router
from app.api.v1.waitlist import router as waitlist_router
from app.api.v1.review import router as review_router
from app.api.v1.content import router as content_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()


api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

api_router.include_router(users_router, prefix="/users", tags=["Users"])

api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])

api_router.include_router(enrollment_router, prefix="/enrollments", tags=["Enrollments"])

api_router.include_router(waitlist_router, prefix="/waitlist", tags=["Waitlist"])

api_router.include_router(review_router, prefix="/reviews", tags=["Reviews"])

api_router.include_router(content_router, prefix="/content", tags=["Course Content"])

api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])