from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.group import group_crud
from app.dependencies.auth import get_current_user, require_admin
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.models.user import User, UserRole


router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=List[GroupResponse])
def get_all_groups(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 100
):
    """Retrieve all groups (Logged-in Users Only)"""
    course_center_id = None
    if current_user.role != UserRole.SUPER_ADMIN:
        course_center_id = current_user.course_center_id
        
    return group_crud.get_all(db, skip=skip, limit=limit, course_center_id=course_center_id)


@router.get("/my-groups", response_model=List[GroupResponse])
def get_my_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve groups for the current logged-in user (Student or Teacher)"""
    return group_crud.get_by_user(db, current_user)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
    group_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a group by ID (Logged-in Users Only)"""
    db_group = group_crud.get_by_id(db, group_id)
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return db_group


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group_in: GroupCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new group (Admin Only)"""
    if admin.role != UserRole.SUPER_ADMIN:
        group_in.course_center_id = admin.course_center_id
        
    return group_crud.create(db, group_in)


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: UUID,
    group_in: GroupUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a group (Admin Only)"""
    updated_group = group_crud.update(db, group_id, group_in)
    if not updated_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: UUID, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a group (Admin Only)"""
    success = group_crud.delete(db, group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return None