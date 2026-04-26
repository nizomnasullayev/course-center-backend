from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.attendance import attendance_crud
from app.crud.lesson import lesson_crud
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_admin
from app.services.telegram_bot import get_telegram_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

async def send_attendance_notification(db: Session, attendance_id: UUID):
    """Background task to send Telegram notification for attendance"""
    service = get_telegram_service()
    
    # Reload record with relationships
    record = attendance_crud.get_by_id(db, attendance_id)
    if not record or not record.student or not record.lesson:
        return

    student = record.student
    lesson = record.lesson
    group_name = lesson.group.name if lesson.group else "Guruh"
    lesson_date = lesson.lesson_date.strftime("%d.%m.%Y")
    
    status_text = "Keldi ✅" if record.status == "present" else "Kelmadi ❌"
    grade_text = f"\n⭐ Bahoingiz: <b>{record.grade}</b>" if record.grade is not None else ""
    
    title = "Davomat xabarnomasi 📚"
    message = (
        f"Hurmatli <b>{student.full_name}</b>,\n\n"
        f"Sizning <b>{lesson_date}</b> kungi <b>{group_name}</b> darsidagi davomatingiz belgilandi:\n\n"
        f"Holat: <b>{status_text}</b>"
        f"{grade_text}\n\n"
        f"O'qishlaringizga omad! 🚀"
    )
    
    await service.notify_user(
        db=db,
        user_id=student.id,
        notification_type="attendance_marked",
        title=title,
        message=message
    )


@router.post("", response_model=AttendanceResponse)
def mark_attendance(
    obj_in: AttendanceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark attendance (Admin or Assigned Teacher only)"""
    lesson = lesson_crud.get_by_id(db, obj_in.lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Permission Check
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN] and lesson.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned teacher or Admin can mark attendance"
        )

    if current_user.role != UserRole.SUPER_ADMIN:
        obj_in.course_center_id = current_user.course_center_id
        
    record = attendance_crud.create(db, obj_in)
    
    # Send Telegram Notification in background
    background_tasks.add_task(send_attendance_notification, db, record.id)
    
    record.student_name = record.student.full_name
    record.student_phone = record.student.phone_number
    return record

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
        r.student_phone = r.student.phone_number
    return records

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: UUID,
    obj_in: AttendanceUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update attendance record (Admin or Assigned Teacher only)"""
    record = attendance_crud.update(db, attendance_id, obj_in)
    if record:
        # Send Telegram Notification in background
        background_tasks.add_task(send_attendance_notification, db, record.id)
        
        record.student_name = record.student.full_name
        record.student_phone = record.student.phone_number
    return record