from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class AttendanceBase(BaseModel):
    lesson_id: UUID
    student_id: UUID
    status: AttendanceStatus = AttendanceStatus.PRESENT
    comment: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    comment: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: UUID
    student_name: Optional[str] = None

    class Config:
        from_attributes = True