from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid


# Junction table for course prerequisites
course_prerequisites = Table(
    "course_prerequisites",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
    Column("prerequisite_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
)


class Course(Base):
    
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    code = Column(String, unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    category = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True, default="Beginner")
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    syllabus_url = Column(String, nullable=True)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    waitlist_entries = relationship("WaitlistEntry", back_populates="course", cascade="all, delete-orphan")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order")
    
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=id == course_prerequisites.c.course_id,
        secondaryjoin=id == course_prerequisites.c.prerequisite_id,
        backref="required_for"
    )