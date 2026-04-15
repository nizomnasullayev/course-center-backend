from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserRole


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
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    role: UserRole = UserRole.STUDENT
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)

    @field_validator('phone_number', 'parents_phone')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        return _validate_phone(v)


class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        return _validate_password(v)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)
    status: Optional[bool] = None

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
    email: Optional[EmailStr] = None
    phone_number: str
    role: UserRole
    parents_phone: Optional[str] = None
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password: Optional[str] = None