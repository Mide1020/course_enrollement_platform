from sqlalchemy.orm import Session
from app.models.lesson import Lesson
from app.schema.lesson import LessonCreate, LessonUpdate
import uuid


class CRUDLesson:

    def create(self, db: Session, lesson: LessonCreate):
        db_lesson = Lesson(
            title=lesson.title,
            content_type=lesson.content_type,
            content_data=lesson.content_data,
            order=lesson.order,
            module_id=lesson.module_id
        )
        db.add(db_lesson)
        return db_lesson

    def get_by_id(self, db: Session, lesson_id: uuid.UUID):
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    def get_by_module(self, db: Session, module_id: uuid.UUID):
        return db.query(Lesson).filter(Lesson.module_id == module_id).order_by(Lesson.order).all()

    def update(self, db: Session, lesson_id: uuid.UUID, lesson_update: LessonUpdate):
        db_lesson = self.get_by_id(db, lesson_id)
        if not db_lesson:
            return None
        
        update_data = lesson_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        
        return db_lesson
    
    def delete(self, db: Session, lesson_id: uuid.UUID):
        db_lesson = self.get_by_id(db, lesson_id)
        if not db_lesson:
            return None
        
        db.delete(db_lesson)
        return db_lesson


lesson_crud = CRUDLesson()
