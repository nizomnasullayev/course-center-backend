from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status

from app.models.attendance import Attendance
from app.models.lesson import Lesson
from app.models.group_student import GroupStudent
from app.models.user import User, UserRole
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate

class AttendanceCRUD:
    def create(self, db: Session, obj_in: AttendanceCreate) -> Attendance:
        # 1. Get the lesson to find out which group it belongs to
        lesson = db.query(Lesson).filter(Lesson.id == obj_in.lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # 2. Verify student is actually enrolled in that specific group
        enrollment = db.query(GroupStudent).filter(
            GroupStudent.group_id == lesson.group_id,
            GroupStudent.student_id == obj_in.student_id
        ).first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student is not enrolled in the group for this lesson"
            )

        db_obj = Attendance(**obj_in.model_dump())
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Attendance already marked for this student")

    def get_by_lesson(self, db: Session, lesson_id: UUID) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.lesson_id == lesson_id).all()

    def update(self, db: Session, attendance_id: UUID, obj_in: AttendanceUpdate) -> Optional[Attendance]:
        db_obj = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

attendance_crud = AttendanceCRUD()