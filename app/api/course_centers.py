from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.course_center import (
    CourseCenterCreate, 
    CourseCenterUpdate, 
    CourseCenterResponse
)
from app.crud.course_center import course_center_crud
from app.models.user import User
from app.dependencies.auth import require_super_admin

router = APIRouter(prefix="/course-centers", tags=["course-centers"])


@router.post("", response_model=CourseCenterResponse, status_code=status.HTTP_201_CREATED)
def create_center(
    center: CourseCenterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Create a new course center (Super Admin only)"""
    return course_center_crud.create(db, center)


@router.get("", response_model=List[CourseCenterResponse])
def get_centers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Get all course centers (Super Admin only)"""
    total, items = course_center_crud.get_all(db, skip=skip, limit=limit, status=status)
    return items


@router.get("/{center_id}", response_model=CourseCenterResponse)
def get_center(
    center_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Get a course center by ID (Super Admin only)"""
    center = course_center_crud.get_by_id(db, center_id)
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course center not found"
        )
    return center


@router.patch("/{center_id}", response_model=CourseCenterResponse)
def update_center(
    center_id: UUID,
    center: CourseCenterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Update a course center (Super Admin only)"""
    updated_center = course_center_crud.update(db, center_id, center)
    if not updated_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course center not found"
        )
    return updated_center


@router.delete("/{center_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_center(
    center_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Delete a course center (Super Admin only)"""
    success = course_center_crud.delete(db, center_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course center not found"
        )
