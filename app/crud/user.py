from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schema.user import UserCreate
from app.core.security import get_password_hash, verify_password
from typing import Optional
import uuid


class CRUDUser:


    def create(self, db: Session, user: UserCreate):

        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Creating user object
        db_user = User(
            email=user.email,
            name=user.name,
            hashed_password=hashed_password,
            role=UserRole(user.role),
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user) 
        return db_user
    
     #get user by email
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    #get user y id
    def get_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        
        return db.query(User).filter(User.id == user_id).first()
    
    #authenticate while loging in
    def authenticate(self, db: Session, email: str, password: str):
        
        # Find user by email
        user = self.get_by_email(db, email)
        
        if not user:
            return None
        
        # password check 
        if not verify_password(password, user.hashed_password):
            return None
        
        #user check
        
        if not user.is_active:
            return None
        
        return user



user_crud = CRUDUser()