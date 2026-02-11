from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.enrollment import Enrollment
from app.schema.enrollment import EnrollmentCreate
from typing import Optional, List
import uuid


class CRUDEnrollment:


    def get_by_id(self, db: Session, enrollment_id: uuid.UUID):
        return db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    def get_by_user_and_course(
        self, 
        db: Session, 
        user_id: uuid.UUID, 
        course_id: uuid.UUID
    ):
        return db.query(Enrollment).filter(
            and_(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Enrollment).offset(skip).limit(limit).all()
    
    def get_by_course(
        self, 
        db: Session, 
        course_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ):
        return db.query(Enrollment).filter(
            Enrollment.course_id == course_id
        ).offset(skip).limit(limit).all()
    
    def count_enrollments_for_course(self, db: Session, course_id: uuid.UUID):
        return db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    
    def create(
        self, 
        db: Session, 
        enrollment: EnrollmentCreate, 
        user_id: uuid.UUID
    ):
        
        db_enrollment = Enrollment(
            user_id=user_id,
            course_id=enrollment.course_id
        )
        
        db.add(db_enrollment)
        db.commit()
        db.refresh(db_enrollment)
        
        return db_enrollment
    
    def delete(self, db: Session, enrollment_id: uuid.UUID):
        db_enrollment = self.get_by_id(db, enrollment_id)
        
        if not db_enrollment:
            return None
        
        db.delete(db_enrollment)
        db.commit()
        
        return db_enrollment


# instance
enrollment_crud = CRUDEnrollment()