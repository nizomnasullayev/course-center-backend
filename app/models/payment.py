import enum
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PaymentType(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    CLICK = "click"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    course_center_id = Column(UUID(as_uuid=True), ForeignKey("course_centers.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    payment_month = Column(String(50), nullable=False)  # e.g., "October 2023"
    type = Column(SQLEnum(PaymentType), nullable=False, default=PaymentType.CASH)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student = relationship("User")
    group = relationship("Group")

    def __repr__(self):
        return f"<Payment(student_id={self.student_id}, amount={self.amount})>"