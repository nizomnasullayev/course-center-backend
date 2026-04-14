from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.group_student import group_student_crud
from app.dependencies.auth import get_current_user, require_admin
from app.schemas.group_student import GroupStudentCreate, GroupStudentResponse
from app.models.user import User

router = APIRouter(prefix="/group-students", tags=["group enrollments"])

@router.post("/enroll", response_model=GroupStudentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(
    enroll_data: GroupStudentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Enroll a student into a group (Admin Only)"""
    return group_student_crud.create(db, enroll_data)


@router.get("/group/{group_id}", response_model=List[GroupStudentResponse])
def get_group_members(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students in a group (Logged-in Users)"""
    students = group_student_crud.get_students_by_group(db, group_id)
    for s in students:
        s.student_name = s.student.full_name
    return students


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_student(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Remove a student from a group (Admin Only)"""
    success = group_student_crud.remove_student_from_group(db, enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment record not found")
    return None