import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class LessonStatus(str, enum.Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    course_center_id = Column(UUID(as_uuid=True), ForeignKey("course_centers.id"), nullable=False)
    
    lesson_date = Column(DateTime, nullable=False)
    topic = Column(String(255), nullable=True)
    status = Column(SQLEnum(LessonStatus), nullable=False, default=LessonStatus.PENDING)

    # Audit timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    group = relationship("Group")
    teacher = relationship("User")

    def __repr__(self):
        return f"<Lesson(id={self.id}, topic='{self.topic}', status={self.status})>"