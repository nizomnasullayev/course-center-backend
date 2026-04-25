from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum
from sqlalchemy.orm import relationship

class NotificationType(str, enum.Enum):
    LESSON_CREATED = "lesson_created"
    LESSON_CANCELLED = "lesson_cancelled"
    LESSON_UPDATED = "lesson_updated"
    ATTENDANCE_MARKED = "attendance_marked"
    PAYMENT_RECORDED = "payment_recorded"
    STUDENT_ENROLLED = "student_enrolled"
    GROUP_UPDATED = "group_updated"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User")