from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.course_center import CourseCenter
from app.schemas.course_center import CourseCenterCreate, CourseCenterUpdate


class CourseCenterCRUD:
    @staticmethod
    def create(db: Session, center_in: CourseCenterCreate) -> CourseCenter:
        from fastapi import HTTPException, status
        from sqlalchemy.exc import IntegrityError
        from app.models.user import User, UserRole
        from app.utils.security import get_password_hash
        
        try:
            db_center = CourseCenter(
                name=center_in.name,
                address=center_in.address,
                phone_number=center_in.phone_number,
                status=center_in.status
            )
            db.add(db_center)
            db.flush() # Get the ID without committing
            
            if center_in.admin:
                hashed_password = get_password_hash(center_in.admin.password)
                db_admin = User(
                    full_name=center_in.admin.full_name,
                    email=center_in.admin.email,
                    phone_number=center_in.admin.phone_number,
                    password=hashed_password,
                    role=UserRole.ADMIN,
                    course_center_id=db_center.id
                )
                db.add(db_admin)
                
            db.commit()
            db.refresh(db_center)
            return db_center
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create course center or admin. Email or phone might already be in use."
            )

    @staticmethod
    def get_by_id(db: Session, center_id: UUID) -> Optional[CourseCenter]:
        return db.query(CourseCenter).filter(CourseCenter.id == center_id).first()

    @staticmethod
    def get_all(
        self,
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[bool] = None
    ) -> Tuple[int, List[CourseCenter]]:
        query = db.query(CourseCenter)
        if status is not None:
            query = query.filter(CourseCenter.status == status)
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    @staticmethod
    def update(db: Session, center_id: UUID, center_in: CourseCenterUpdate) -> Optional[CourseCenter]:
        db_center = CourseCenterCRUD.get_by_id(db, center_id)
        if not db_center:
            return None
        
        update_data = center_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_center, field, value)
        
        db.commit()
        db.refresh(db_center)
        return db_center

    @staticmethod
    def delete(db: Session, center_id: UUID) -> bool:
        db_center = CourseCenterCRUD.get_by_id(db, center_id)
        if not db_center:
            return False
        
        db.delete(db_center)
        db.commit()
        return True


course_center_crud = CourseCenterCRUD()
