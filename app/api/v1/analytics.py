from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import uuid

from app.database import get_db
from app.api import deps
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.review import Review
from app.models.user import User

router = APIRouter()

@router.get("/instructor/dashboard")
def get_instructor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_instructor)
):
    """
    Get instructor dashboard analytics.
    Returns:
    - Total students across all courses.
    - Enrollment breakdown per course.
    - Average rating per course.
    """
    # Efficiently fetch course stats in a single query
    # We join courses with enrollments and reviews to get counts and averages
    stats_query = db.query(
        Course.id,
        Course.title,
        Course.code,
        func.count(func.distinct(Enrollment.id)).filter(Enrollment.status == EnrollmentStatus.ENROLLED).label("enrollment_count"),
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Enrollment, Course.id == Enrollment.course_id)\
     .outerjoin(Review, Course.id == Review.course_id)\
     .filter(Course.instructor_id == current_user.id)\
     .group_by(Course.id)\
     .all()

    course_stats = []
    total_students = 0
    
    for row in stats_query:
        enroll_count = row.enrollment_count or 0
        total_students += enroll_count
        
        course_stats.append({
            "course_id": row.id,
            "course_title": row.title,
            "course_code": row.code,
            "enrollment_count": enroll_count,
            "average_rating": round(float(row.avg_rating or 0.0), 2)
        })
        
    return {
        "instructor_name": current_user.name,
        "total_courses": len(course_stats),
        "total_active_students": total_students,
        "course_breakdown": course_stats
    }

