from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash
from fastapi import HTTPException, status


class UserCRUD:
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """Create a new user"""
        hashed_password = None
        if user_in.password:
            hashed_password = get_password_hash(user_in.password)
        
        db_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            phone_number=user_in.phone_number,
            password=hashed_password,
            role=user_in.role,
            course_center_id=user_in.course_center_id,
            parents_phone=user_in.parents_phone,
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or phone number already exists"
            )

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_phone(db: Session, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return db.query(User).filter(User.phone_number == phone_number).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email address"""
        
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[bool] = None,
        course_center_id: Optional[UUID] = None
    ) -> tuple[int, List[User]]:
        """Get all users with optional filters"""
        # Hide super admins from all lists
        query = db.query(User).filter(User.role != UserRole.SUPER_ADMIN)
        
        if role is not None:
            query = query.filter(User.role == role)

        
        if status is not None:
            query = query.filter(User.status == status)

        if course_center_id is not None:
            query = query.filter(User.course_center_id == course_center_id)
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    @staticmethod
    def update(db: Session, user_id: UUID, user_in: UserUpdate) -> Optional[User]:
        """Update a user"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )

    @staticmethod
    def delete(db: Session, user_id: UUID) -> bool:
        """Delete a user (hard delete)"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def deactivate(db: Session, user_id: UUID) -> Optional[User]:
        """Deactivate a user (soft delete)"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.status = False
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def activate(db: Session, user_id: UUID) -> Optional[User]:
        """Activate a user"""
        db_user = UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.status = True
        db.commit()
        db.refresh(db_user)
        return db_user


user_crud = UserCRUD()