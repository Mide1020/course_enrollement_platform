from sqlalchemy.orm import Session
from app.models.review import Review
from app.schema.review import ReviewCreate
import uuid
from typing import List


class CRUDReview:
    
    def get_by_id(self, db: Session, review_id: uuid.UUID):
        return db.query(Review).filter(Review.id == review_id).first()
    
    def get_by_course(self, db: Session, course_id: uuid.UUID, skip: int = 0, limit: int = 100):
        return db.query(Review).filter(Review.course_id == course_id).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_id: uuid.UUID, course_id: uuid.UUID, enrollment_id: uuid.UUID, review: ReviewCreate):
        db_review = Review(
            user_id=user_id,
            course_id=course_id,
            enrollment_id=enrollment_id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(db_review)
        return db_review

    def delete(self, db: Session, review_id: uuid.UUID):
        db_review = self.get_by_id(db, review_id)
        if db_review:
            db.delete(db_review)
        return db_review


review_crud = CRUDReview()
