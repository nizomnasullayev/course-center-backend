from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud.user import user_crud
from app.models.user import UserRole, User
from app.dependencies import get_current_user, require_admin, require_teacher

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admins can create users
):
    """Create a new user (Admin only)"""
    return user_crud.create(db, user)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user's information"""
    return current_user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = None,
    status: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)  # Teachers and admins can list users
):
    """Get all users with optional filters (Teachers and Admins)"""
    return user_crud.get_all(db, skip=skip, limit=limit, role=role, status=status)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get a user by ID (Teachers and Admins)"""
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/phone/{phone_number}", response_model=UserResponse)
def get_user_by_phone(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get a user by phone number (Teachers and Admins)"""
    user = user_crud.get_by_phone(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user
    - Users can update their own info (except role and status)
    - Admins can update anyone's info
    """
    # Check permissions
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Non-admins cannot change role or status
    if current_user.role != UserRole.ADMIN:
        if user.role is not None or user.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change role or status"
            )
    
    updated_user = user_crud.update(db, user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admins can delete
):
    """Delete a user (hard delete) - Admin only"""
    success = user_crud.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admins can deactivate
):
    """Deactivate a user (soft delete) - Admin only"""
    user = user_crud.deactivate(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admins can activate
):
    """Activate a user - Admin only"""
    user = user_crud.activate(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user