from sqlalchemy.orm import Session
from app.models.course import Course
from app.schema.course import CourseCreate, CourseUpdate
from typing import Optional, List
import uuid


class CRUDCourse:

#crudcreate course
    def create(self, db: Session, course: CourseCreate):
        db_course = Course(
            title=course.title,
            code=course.code,
            capacity=course.capacity,
            is_active=True
        )
        
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        
        return db_course
    #crudget course by id
    def get_by_id(self, db: Session, course_id: uuid.UUID):
        return db.query(Course).filter(Course.id == course_id).first()
    
    #crudgetcourse by course code
    def get_by_code(self, db: Session, code: str):
        return db.query(Course).filter(Course.code == code).first()
    
    #crud get all active course
    def get_all_active(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()
    

     #crud get all course
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Course).offset(skip).limit(limit).all()


     #crud update course    
    def update(self, db: Session, course_id: uuid.UUID, course_update: CourseUpdate):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        # Update only provided fields
        update_data = course_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_course, field, value)
        
        db.commit()
        db.refresh(db_course)
        
        return db_course
    
    def delete(self, db: Session, course_id: uuid.UUID):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        #Soft delete 
        db_course.is_active = False
        
        db.commit()
        db.refresh(db_course)
        
        return db_course
    
    def activate(self, db: Session, course_id: uuid.UUID):
        db_course = self.get_by_id(db, course_id)
        
        if not db_course:
            return None
        
        db_course.is_active = True
        
        db.commit()
        db.refresh(db_course)
        
        return db_course

course_crud = CRUDCourse()