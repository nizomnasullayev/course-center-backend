from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class GroupStatus(str, enum.Enum):
    ACTIVE = "active"
    FINISHED = "finished"

class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    subject_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    price: float = Field(..., gt=0)
    schedule: str = Field(..., description="e.g., Mon-Wed-Fri 18:00")
    start_date: datetime
    status: GroupStatus = GroupStatus.ACTIVE


class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    subject_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    price: Optional[float] = None
    schedule: Optional[str] = None
    start_date: Optional[datetime] = None
    status: Optional[GroupStatus] = None

    
class SubjectSimple(BaseModel):
    id: UUID
    name: str
    class Config:
        from_attributes = True

class TeacherSimple(BaseModel):
    id: UUID
    full_name: str
    class Config:
        from_attributes = True

class GroupResponse(GroupBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    subject: Optional[SubjectSimple] = None
    teacher: Optional[TeacherSimple] = None

    class Config:
        from_attributes = True