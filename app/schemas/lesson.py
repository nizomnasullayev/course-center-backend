from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import enum

class LessonStatus(str, enum.Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class LessonBase(BaseModel):
    group_id: UUID
    teacher_id: Optional[UUID] = None
    lesson_date: datetime
    topic: Optional[str] = Field(None, max_length=255)
    status: LessonStatus = LessonStatus.PENDING
    course_center_id: Optional[UUID] = None

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    teacher_id: Optional[UUID] = None
    lesson_date: Optional[datetime] = None
    topic: Optional[str] = None
    status: Optional[LessonStatus] = None

class LessonResponse(LessonBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    group_name: Optional[str] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


class LessonPaginationResponse(BaseModel):
    total: int
    items: List[LessonResponse]