from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime

from app.models.lesson import Lesson, LessonStatus
from app.models.group import Group
from app.models.user import User, UserRole
from app.schemas.lesson import LessonCreate, LessonUpdate
from app.services.notification_helpers import NotificationHelper
from app.services.background_tasks import background_task

class LessonCRUD:
    def create(self, db: Session, lesson_in: LessonCreate) -> Lesson:
        # 1. If teacher_id is empty, grab the default teacher from the group
        teacher_id = lesson_in.teacher_id
        if not teacher_id:
            group = db.query(Group).filter(Group.id == lesson_in.group_id).first()
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
            teacher_id = group.teacher_id

        # 2. Verify the teacher exists and has the correct role
        if teacher_id:
            teacher = db.query(User).filter(User.id == teacher_id).first()
            if not teacher or teacher.role != UserRole.TEACHER:
                raise HTTPException(
                    status_code=400, 
                    detail="Assigned user is not a teacher or does not exist"
                )

        db_obj = Lesson(
            group_id=lesson_in.group_id,
            teacher_id=teacher_id,
            lesson_date=lesson_in.lesson_date,
            topic=lesson_in.topic,
            status=lesson_in.status
        )
        
        @background_task
        async def send_notification():
            await NotificationHelper.notify_lesson_created(db, db_obj.id)
        
        send_notification()

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_group(self, db: Session, group_id: UUID) -> List[Lesson]:
        """Get all lessons for a specific group"""
        return db.query(Lesson).filter(Lesson.group_id == group_id).order_by(Lesson.lesson_date).all()

    def get_all_paginated(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[int, List[Lesson]]:
        """Get all lessons globally with pagination"""
        query = db.query(Lesson).order_by(Lesson.lesson_date.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return total, items

    def get_by_id(self, db: Session, lesson_id: UUID) -> Optional[Lesson]:
        return db.query(Lesson).filter(Lesson.id == lesson_id).first()

    def update(self, db: Session, lesson_id: UUID, lesson_in: LessonUpdate) -> Optional[Lesson]:

        old_lesson = self.get_by_id(db, lesson_id)

        db_obj = self.get_by_id(db, lesson_id)
        if not db_obj:
            return None
        
        update_data = lesson_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        if (lesson_in.status and 
            lesson_in.status == LessonStatus.CANCELLED and 
            old_lesson.status != LessonStatus.CANCELLED):
            
            @background_task
            async def send_cancellation():
                await NotificationHelper.notify_lesson_cancelled(db, lesson_id)
            
            send_cancellation()

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, lesson_id: UUID) -> bool:
        db_obj = self.get_by_id(db, lesson_id)
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True

lesson_crud = LessonCRUD()