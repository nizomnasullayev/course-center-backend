from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectCRUD:
    @staticmethod
    def create(db: Session, subject_in: SubjectCreate) -> Subject:
        """Create a new subject"""
        db_subject = Subject(
            name=subject_in.name,
            description=subject_in.description
        )
        
        try:
            db.add(db_subject)
            db.commit()
            db.refresh(db_subject)
            return db_subject
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject with this name already exists"
            )

    @staticmethod
    def get_by_id(db: Session, subject_id: UUID) -> Optional[Subject]:
        """Get subject by ID"""
        return db.query(Subject).filter(Subject.id == subject_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Subject]:
        """Get subject by exact name"""
        return db.query(Subject).filter(Subject.name == name).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subject]:
        """Get all subjects with pagination"""
        return db.query(Subject).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, subject_id: UUID, subject_in: SubjectUpdate) -> Optional[Subject]:
        """Update a subject"""
        db_subject = SubjectCRUD.get_by_id(db, subject_id)
        if not db_subject:
            return None
        
        # Exclude unset fields so we don't overwrite existing data with None
        update_data = subject_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_subject, field, value)
        
        try:
            db.commit()
            db.refresh(db_subject)
            return db_subject
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject name already in use"
            )

    @staticmethod
    def delete(db: Session, subject_id: UUID) -> bool:
        """Delete a subject (hard delete)"""
        db_subject = SubjectCRUD.get_by_id(db, subject_id)
        if not db_subject:
            return False
        
        db.delete(db_subject)
        db.commit()
        return True


subject_crud = SubjectCRUD()