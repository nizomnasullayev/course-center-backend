from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class GroupStudentBase(BaseModel):
    group_id: UUID
    student_id: UUID

class GroupStudentCreate(GroupStudentBase):
    joined_date: Optional[datetime] = None

class GroupStudentResponse(GroupStudentBase):
    id: UUID
    joined_date: datetime
    created_at: datetime
    
    # We can include the student's name for the frontend friend
    student_name: Optional[str] = None 

    class Config:
        from_attributes = True