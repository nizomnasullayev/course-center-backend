from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.payment import payment_crud
from app.crud.group import group_crud
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentPaginationResponse
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("", response_model=PaymentPaginationResponse)
def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Retrieve all payments globally (Admin only)"""
    total, items = payment_crud.get_all(db, skip=skip, limit=limit)
    for p in items:
        p.student_name = p.student.full_name
        p.group_name = p.group.name if p.group else "General"
    return {"total": total, "items": items}

@router.post("", response_model=PaymentResponse)
def record_payment(
    obj_in: PaymentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Record a new payment (Admin Only)"""
    return payment_crud.create(db, obj_in)

@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Students see their own history"""
    payments = payment_crud.get_by_student(db, current_user.id)
    for p in payments:
        p.student_name = p.student.full_name
        p.group_name = p.group.name if p.group else "General"
    return payments

@router.get("/group/{group_id}", response_model=List[PaymentResponse])
def get_group_payments(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admins see all; Teachers see only their assigned group's payments"""
    group = group_crud.get_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user.role != UserRole.ADMIN and group.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to see this group's financial data")

    payments = payment_crud.get_by_group(db, group_id)
    for p in payments:
        p.student_name = p.student.full_name
        p.group_name = group.name
    return payments