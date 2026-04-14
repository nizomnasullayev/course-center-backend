import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class GroupStatus(str, enum.Enum):
    ACTIVE = "active"
    FINISHED = "finished"

class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    schedule = Column(String(255), nullable=False) # e.g., "Mon-Wed-Fri 18:00"
    start_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(GroupStatus), nullable=False, default=GroupStatus.ACTIVE)
    
    # Foreign Keys
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (makes it easy to do group.teacher.full_name)
    subject = relationship("Subject")
    teacher = relationship("User")
    students = relationship("GroupStudent", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', status={self.status})>"