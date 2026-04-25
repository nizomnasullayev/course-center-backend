from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    parents_phone = Column(String(20), nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    telegram_chat_id = Column(String(50), unique=True, nullable=True, index=True)
    telegram_link_token = Column(String(100), unique=True, nullable=True, index=True)
    telegram_link_expires_at = Column(DateTime, nullable=True)  # Token expiration
    telegram_notifications_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    
    __table_args__ = (
        Index('ix_users_role_status', 'role', 'status'),
        Index('ix_users_created_at', 'created_at'),
        Index('ix_users_email', 'email'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, full_name='{self.full_name}', role={self.role})>"