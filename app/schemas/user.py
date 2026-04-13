from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=5, max_length=20)
    role: UserRole = UserRole.STUDENT
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)

    @field_validator('phone_number', 'parents_phone')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Basic international phone validation (allows +, digits, spaces, dashes, parentheses)
        pattern = r'^\+?[\d\s\-\(\)]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format')
        # Remove spaces and dashes for storage
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        if len(cleaned) < 5:
            raise ValueError('Phone number too short')
        return v


class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v  # Allowed for Google auth users
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=5, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    parents_phone: Optional[str] = Field(None, min_length=5, max_length=20)
    status: Optional[bool] = None

    @field_validator('phone_number', 'parents_phone')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r'^\+?[\d\s\-\(\)]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format')
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        if len(cleaned) < 5:
            raise ValueError('Phone number too short')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserResponse(UserBase):
    id: UUID
    status: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    password: Optional[str]  # Include hashed password for internal use