from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.waitlist import WaitlistEntry
from typing import Optional, List
import uuid


class CRUDWaitlist:

    def get_by_id(self, db: Session, entry_id: uuid.UUID):
        return db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
    
    def get_by_user_and_course(
        self, 
        db: Session, 
        user_id: uuid.UUID, 
        course_id: uuid.UUID
    ):
        return db.query(WaitlistEntry).filter(
            and_(
                WaitlistEntry.user_id == user_id,
                WaitlistEntry.course_id == course_id
            )
        ).first()
    
    def get_by_course(self, db: Session, course_id: uuid.UUID):
        return db.query(WaitlistEntry).filter(
            WaitlistEntry.course_id == course_id
        ).order_by(WaitlistEntry.created_at.asc()).all()
    
    def count_by_course(self, db: Session, course_id: uuid.UUID):
        return db.query(WaitlistEntry).filter(WaitlistEntry.course_id == course_id).count()

    def create(self, db: Session, user_id: uuid.UUID, course_id: uuid.UUID):
        db_entry = WaitlistEntry(
            user_id=user_id,
            course_id=course_id
        )
        db.add(db_entry)
        # db.commit() and db.refresh() removed for transaction management in API layer
        return db_entry
    
    def delete(self, db: Session, entry_id: uuid.UUID):
        db_entry = self.get_by_id(db, entry_id)
        if not db_entry:
            return None
        db.delete(db_entry)
        # db.commit() removed for transaction management in API layer
        return db_entry

    def remove_user_from_course_waitlist(self, db: Session, user_id: uuid.UUID, course_id: uuid.UUID):
        db_entry = self.get_by_user_and_course(db, user_id, course_id)
        if db_entry:
            db.delete(db_entry)
            # db.commit() removed for transaction management in API layer
            return True
        return False

waitlist_crud = CRUDWaitlist()
