import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class GroupStudent(Base):
    __tablename__ = "group_students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # When the student actually started the course
    joined_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Audit timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    group = relationship("Group", back_populates="students")
    student = relationship("User")

    # Prevent a student from being added to the same group twice
    __table_args__ = (
        UniqueConstraint('group_id', 'student_id', name='_group_student_uc'),
    )

    def __repr__(self):
        return f"<GroupStudent(group_id={self.group_id}, student_id={self.student_id})>"