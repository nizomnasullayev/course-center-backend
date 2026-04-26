from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class CenterAdminCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)


class CourseCenterBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone_number: Optional[str] = None
    status: bool = True


class CourseCenterCreate(CourseCenterBase):
    admin: Optional[CenterAdminCreate] = None


class CourseCenterUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[bool] = None


class CourseCenterResponse(CourseCenterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
