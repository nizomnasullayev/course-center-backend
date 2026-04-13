from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.crud.subject import subject_crud
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectResponse])
def get_all_subjects(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100
):
    """Retrieve all subjects (Public)"""
    return subject_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: UUID, db: Session = Depends(get_db)):
    """Get a subject by ID (Public)"""
    db_subject = subject_crud.get_by_id(db, subject_id)
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return db_subject


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create a new subject (Admin Only)"""
    return subject_crud.create(db, subject_in)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: UUID,
    subject_in: SubjectUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a subject (Admin Only)"""
    updated_subject = subject_crud.update(db, subject_id, subject_in)
    if not updated_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return updated_subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: UUID, 
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a subject (Admin Only)"""
    success = subject_crud.delete(db, subject_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return None