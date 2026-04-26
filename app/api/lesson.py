from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.lesson import lesson_crud
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse, LessonPaginationResponse
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/lessons", tags=["lessons"])

@router.get("", response_model=LessonPaginationResponse)
def get_all_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Retrieve all lessons globally (Admin only)"""
    course_center_id = None
    if current_user.role != UserRole.SUPER_ADMIN:
        course_center_id = current_user.course_center_id
        
    total, items = lesson_crud.get_all_paginated(db, skip=skip, limit=limit, course_center_id=course_center_id)
    # Join additional info
    for lesson in items:
        lesson.group_name = lesson.group.name
        lesson.teacher_name = lesson.teacher.full_name if lesson.teacher else "No Teacher"
    return {"total": total, "items": items}

@router.get("/group/{group_id}", response_model=List[LessonResponse])
def get_group_lessons(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all lessons for a specific group"""
    lessons = lesson_crud.get_by_group(db, group_id)
    for lesson in lessons:
        lesson.group_name = lesson.group.name
        lesson.teacher_name = lesson.teacher.full_name if lesson.teacher else "No Teacher"
    return lessons

@router.post("", response_model=LessonResponse)
def create_lesson(
    lesson_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a lesson (Admin or the Teacher assigned to this group)"""
    if current_user.role != UserRole.ADMIN:
        from app.crud.group import group_crud
        group = group_crud.get_by_id(db, lesson_in.group_id)
        if not group or group.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned teacher or an Admin can create lessons for this group."
            )
            
    if current_user.role != UserRole.SUPER_ADMIN:
        lesson_in.course_center_id = current_user.course_center_id
        
    return lesson_crud.create(db, lesson_in)

@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: UUID,
    lesson_in: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a lesson (Admin or the specific teacher assigned to the lesson)"""
    db_lesson = lesson_crud.get_by_id(db, lesson_id)
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    if current_user.role != UserRole.ADMIN and db_lesson.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this lesson."
        )

    return lesson_crud.update(db, lesson_id, lesson_in)

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a lesson (Admin Only)"""
    if not lesson_crud.delete(db, lesson_id):
        raise HTTPException(status_code=404, detail="Lesson not found")
    return None