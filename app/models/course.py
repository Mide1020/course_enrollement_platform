from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid


class Course(Base):
    
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")