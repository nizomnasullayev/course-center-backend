from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserRole


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    v = v.strip()
    if not _EMAIL_RE.match(v):
        raise ValueError("Invalid email address")
    return v


def _validate_phone(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    pattern = r'^\+?[\d\s\-\(\)]+$'
    if not re.match(pattern, v):
        raise ValueError('Invalid phone number format')
    cleaned = re.sub(r'[\s\-\(\)]', '', v)
    if len(cleaned) < 5:
        raise ValueError('Phone number too short')
    return cleaned


def _validate_password(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters')
    return v


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    # Keep validation lightweight and allow internal domains like *.local.
    email: str
    phone_number: str = Field(..., min_length=5, max_length=20)
    role: UserRole = UserRole.STUDENT
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return _validate_email(v)  # type: ignore[return-value]

    @field_validator('phone_number', 'parents_phone')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        return _validate_phone(v)


class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    course_center_id: Optional[UUID] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        return _validate_password(v)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    course_center_id: Optional[UUID] = None
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)
    status: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        return _validate_email(v)

    @field_validator('phone_number', 'parents_phone')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        return _validate_phone(v)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        return _validate_password(v)


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    # Response should not 500 on already-stored internal/test emails (e.g. *.local).
    email: Optional[str] = None
    phone_number: str
    role: UserRole
    course_center_id: Optional[UUID] = None
    parents_phone: Optional[str] = None
    status: bool
    telegram_chat_id: Optional[str] = None
    telegram_notifications_enabled: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPaginationResponse(BaseModel):
    total: int
    items: List[UserResponse]


class UserInDB(UserResponse):
    password: Optional[str] = None
