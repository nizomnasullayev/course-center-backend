from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status

from app.models.payment import Payment
from app.models.user import User, UserRole
from app.models.group_student import GroupStudent
from app.schemas.payment import PaymentCreate

class PaymentCRUD:
    def create(self, db: Session, obj_in: PaymentCreate) -> Payment:
        # 1. Verify student exists and is actually a student
        student = db.query(User).filter(User.id == obj_in.student_id).first()
        if not student or student.role != UserRole.STUDENT:
            raise HTTPException(status_code=400, detail="Invalid student ID or user is not a student")

        # 2. Verify student is enrolled in the group (if group_id is provided)
        if obj_in.group_id:
            enrollment = db.query(GroupStudent).filter(
                GroupStudent.group_id == obj_in.group_id,
                GroupStudent.student_id == obj_in.student_id
            ).first()
            if not enrollment:
                raise HTTPException(status_code=400, detail="Student is not enrolled in this group")

        db_obj = Payment(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_student(self, db: Session, student_id: UUID) -> List[Payment]:
        return db.query(Payment).filter(Payment.student_id == student_id).all()

    def get_by_group(self, db: Session, group_id: UUID) -> List[Payment]:
        return db.query(Payment).filter(Payment.group_id == group_id).all()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        return db.query(Payment).offset(skip).limit(limit).all()

payment_crud = PaymentCRUD()