from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status

from app.models.group_student import GroupStudent
from app.models.user import User, UserRole
from app.schemas.group_student import GroupStudentCreate

class GroupStudentCRUD:
    def create(self, db: Session, obj_in: GroupStudentCreate) -> GroupStudent:
        # 1. Verify the user exists AND has the STUDENT role
        student = db.query(User).filter(User.id == obj_in.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="User not found")
        
        if student.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {student.full_name} is a {student.role}, not a student."
            )

        # 2. Try to enroll
        db_obj = GroupStudent(
            group_id=obj_in.group_id,
            student_id=obj_in.student_id,
            joined_date=obj_in.joined_date or datetime.utcnow()
        )
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, 
                detail="Student is already enrolled in this group."
            )

    def get_students_by_group(self, db: Session, group_id: UUID) -> List[GroupStudent]:
        """Get all students enrolled in a specific group"""
        return db.query(GroupStudent).filter(GroupStudent.group_id == group_id).all()

    def remove_student_from_group(self, db: Session, enrollment_id: UUID) -> bool:
        """Unenroll a student"""
        db_obj = db.query(GroupStudent).filter(GroupStudent.id == enrollment_id).first()
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True

group_student_crud = GroupStudentCRUD()