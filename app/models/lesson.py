from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # e.g., 'video', 'text', 'file'
    content_data = Column(Text, nullable=True)     # URL or markdown text
    order = Column(Integer, default=0)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    resource_url = Column(String, nullable=True)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
