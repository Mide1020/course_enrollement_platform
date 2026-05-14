from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.course import Course
from app.models.review import Review
from app.schema.course import CourseCreate, CourseUpdate
from typing import Optional, List
import uuid


class CRUDCourse:

    def create(self, db: Session, course: CourseCreate):
        db_course = Course(
            title=course.title,
            code=course.code,
            capacity=course.capacity,
            category=course.category,
            difficulty_level=course.difficulty_level,
            syllabus_url=course.syllabus_url,
            instructor_id=course.instructor_id,
            is_active=True
        )
        
        # Handle prerequisites
        if course.prerequisite_ids:
            prereqs = db.query(Course).filter(Course.id.in_(course.prerequisite_ids)).all()
            db_course.prerequisites = prereqs
            
        db.add(db_course)
        # db.commit() and db.refresh() removed for transaction management in API layer
        
        return db_course

    def get_by_id(self, db: Session, course_id: uuid.UUID):
        return db.query(Course).filter(Course.id == course_id).first()
    
    def get_by_code(self, db: Session, code: str):
        return db.query(Course).filter(Course.code == code).first()
    
    def get_all_active(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_rating: Optional[float] = None
    ):
        query = db.query(Course).filter(Course.is_active == True)
        
        if search:
            query = query.filter(
                or_(
                    Course.title.ilike(f"%{search}%"),
                    Course.code.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(Course.category == category)
            
        if difficulty:
            query = query.filter(Course.difficulty_level == difficulty)
            
        if min_rating:
            # Join with reviews and filter by average rating
            avg_rating_subquery = db.query(
                Review.course_id,
                func.avg(Review.rating).label("avg_rating")
            ).group_by(Review.course_id).subquery()
            
            query = query.join(
                avg_rating_subquery,
                Course.id == avg_rating_subquery.c.course_id
            ).filter(avg_rating_subquery.c.avg_rating >= min_rating)
            
        return query.offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Course).offset(skip).limit(limit).all()

    def update(self, db: Session, course_id: uuid.UUID, course_update: CourseUpdate):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        # Update fields
        update_data = course_update.model_dump(exclude_unset=True)
        
        if "prerequisite_ids" in update_data:
            prereq_ids = update_data.pop("prerequisite_ids")
            if prereq_ids is not None:
                prereqs = db.query(Course).filter(Course.id.in_(prereq_ids)).all()
                db_course.prerequisites = prereqs
        
        for field, value in update_data.items():
            setattr(db_course, field, value)
        
        # db.commit() and db.refresh() removed for transaction management in API layer
        
        return db_course
    
    def delete(self, db: Session, course_id: uuid.UUID):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        # Soft delete 
        db_course.is_active = False
        
        # db.commit() and db.refresh() removed for transaction management in API layer
        
        return db_course
    
    def activate(self, db: Session, course_id: uuid.UUID):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        db_course.is_active = True
        
        # db.commit() and db.refresh() removed for transaction management in API layer
        
        return db_course

    def get_by_instructor(self, db: Session, instructor_id: uuid.UUID):
        return db.query(Course).filter(Course.instructor_id == instructor_id).all()

course_crud = CRUDCourse()