from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.attendance import attendance_crud
from app.crud.lesson import lesson_crud
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("", response_model=AttendanceResponse)
def mark_attendance(
    obj_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark attendance (Admin or Assigned Teacher only)"""
    lesson = lesson_crud.get_by_id(db, obj_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Permission Check
    if current_user.role != UserRole.ADMIN and lesson.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned teacher or Admin can mark attendance"
        )
    
    return attendance_crud.create(db, obj_in)

@router.get("/lesson/{lesson_id}", response_model=List[AttendanceResponse])
def get_lesson_attendance(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View attendance for a lesson (Admins, Teachers, or enrolled Students)"""
    records = attendance_crud.get_by_lesson(db, lesson_id)
    for r in records:
        r.student_name = r.student.full_name
    return records

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: UUID,
    obj_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update attendance record (Admin or Assigned Teacher only)"""
    return attendance_crud.update(db, attendance_id, obj_in)