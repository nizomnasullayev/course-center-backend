from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status

from app.models.group import Group
from app.models.user import User, UserRole
from app.schemas.group import GroupCreate, GroupUpdate
from app.services.background_tasks import background_task
from app.services.notification_helpers import NotificationHelper

class GroupCRUD:
    def _verify_teacher(self, db: Session, teacher_id: Optional[UUID]):
        """Helper to ensure the assigned teacher exists and has the correct role"""
        if teacher_id:
            teacher = db.query(User).filter(User.id == teacher_id).first()
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Teacher not found"
                )
            if teacher.role != UserRole.TEACHER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {teacher.full_name} is not a teacher (Role: {teacher.role})"
                )

    def create(self, db: Session, group_in: GroupCreate) -> Group:
        # Check if the teacher is actually a teacher
        self._verify_teacher(db, group_in.teacher_id)
        
        db_group = Group(**group_in.model_dump())
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        course_center_id: Optional[UUID] = None
    ) -> List[Group]:
        query = db.query(Group)
        if course_center_id:
            query = query.filter(Group.course_center_id == course_center_id)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, group_id: UUID) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()

    def update(self, db: Session, group_id: UUID, group_in: GroupUpdate) -> Optional[Group]:
        db_group = self.get_by_id(db, group_id)
        if not db_group:
            return None
        
        update_data = group_in.model_dump(exclude_unset=True)
        
        if "teacher_id" in update_data:
            self._verify_teacher(db, update_data["teacher_id"])
        
        for field, value in update_data.items():
            setattr(db_group, field, value)
            
        db.commit()
        db.refresh(db_group)
        
        # TODO: Add notification back later
        # if changes:
        #     from app.services.notification_helpers import NotificationHelper
        #     # send notification
        
        return db_group

    def delete(self, db: Session, group_id: UUID) -> bool:
        db_group = self.get_by_id(db, group_id)
        if not db_group:
            return False
        db.delete(db_group)
        db.commit()
        return True

group_crud = GroupCRUD()