# app/services/notification_helpers.py
import logging
from sqlalchemy.orm import Session
from uuid import UUID
from app.services.telegram_bot import get_telegram_service

logger = logging.getLogger(__name__)


class NotificationHelper:
    
    @staticmethod
    async def notify_lesson_created(db: Session, lesson_id: UUID):
        """Notify students when a new lesson is scheduled"""
        try:
            from app.crud.lesson import lesson_crud
            from app.crud.group import group_crud
            from app.models.group_student import GroupStudent
            
            lesson = lesson_crud.get_by_id(db, lesson_id)
            if not lesson:
                return
            
            group = group_crud.get_by_id(db, lesson.group_id)
            if not group:
                return
            
            title = "📚 New Lesson Scheduled"
            message = f"""
Group: {group.name}
Subject: {group.subject.name if group.subject else 'N/A'}
Topic: {lesson.topic or 'No topic specified'}
Date: {lesson.lesson_date.strftime('%Y-%m-%d %H:%M')}
Status: {lesson.status.value.upper()}
            """
            
            service = get_telegram_service()
            
            # Get all students in group
            students = db.query(GroupStudent).filter(
                GroupStudent.group_id == lesson.group_id
            ).all()
            
            for enrollment in students:
                await service.notify_user(
                    db, enrollment.student_id, "lesson_created", title, message
                )
        except Exception as e:
            logger.error(f"Error in notify_lesson_created: {e}")
    
    @staticmethod
    async def notify_student_enrolled(db: Session, enrollment_id: UUID):
        """Welcome message when student is added to group"""
        try:
            from app.models.group_student import GroupStudent
            
            enrollment = db.query(GroupStudent).filter(
                GroupStudent.id == enrollment_id
            ).first()
            
            if not enrollment:
                return
            
            title = "🎉 Welcome to the Group!"
            message = f"""
Hello {enrollment.student.full_name}!

You have been enrolled in:
📖 <b>Group:</b> {enrollment.group.name}
💰 <b>Price:</b> ${enrollment.group.price:,.2f}
📅 <b>Schedule:</b> {enrollment.group.schedule}
🚀 <b>Start Date:</b> {enrollment.group.start_date.strftime('%Y-%m-%d')}

We're excited to have you!
            """
            
            service = get_telegram_service()
            await service.notify_user(
                db, enrollment.student_id, "student_enrolled", title, message
            )
        except Exception as e:
            logger.error(f"Error in notify_student_enrolled: {e}")
    
    # Add more notification methods as needed
    @staticmethod
    @staticmethod
    async def notify_attendance_marked(db: Session, attendance_id: UUID):
        """Send formatted attendance notification to student"""
        from app.models.attendance import Attendance
        from app.services.telegram_bot import get_telegram_service
        
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance or not attendance.student.telegram_chat_id:
            return
        
        status_emoji = {
            "present": "✅",
            "absent": "❌",
            "late": "⏰"
        }.get(attendance.status.value, "📝")
        
        status_text = {
            "present": "Keldi",
            "absent": "Kelolmadi", 
            "late": "Kechikdi"
        }.get(attendance.status.value, attendance.status.value)
        
        comment = attendance.comment if attendance.comment else "Davomat bo'yicha qo'shimcha izoh qoldirilmagan."
        
        message = f"""📍 <b>Sizning davomatingiz yangilandi!</b>

📚 <b>Guruh:</b> {attendance.lesson.group.name}
📘 <b>Dars:</b> {attendance.lesson.topic or 'Mavzu belgilanmagan'}
🕒 <b>Para:</b> {attendance.lesson.lesson_date.strftime('%H:%M')}
📅 <b>Sana:</b> {attendance.lesson.lesson_date.strftime('%d.%m.%Y')}
{status_emoji} <b>Holat:</b> {status_text}
📝 <b>Izoh:</b> {comment}

Barakalla, bugungi darsda qatnashdingiz va bu juda muhim! 🎉"""
        
        service = get_telegram_service()
        await service.send_message(attendance.student.telegram_chat_id, message)
    
    @staticmethod
    async def notify_grade_updated(db: Session, grade_id: UUID):
        """Send formatted grade notification to student"""
        from app.models.grade import Grade
        from app.services.telegram_bot import get_telegram_service
        
        grade = db.query(Grade).filter(Grade.id == grade_id).first()
        if not grade or not grade.student.telegram_chat_id:
            return
        
        # Calculate star rating
        stars = "★" * int(grade.percentage / 20) + "☆" * (5 - int(grade.percentage / 20))
        
        # Generate feedback text based on percentage
        if grade.percentage >= 90:
            feedback = "A'lo! Siz juda yaxshi natijaga erishdingiz!"
        elif grade.percentage >= 70:
            feedback = "Yaxshi! Siz yaxshi natija ko'rsatdingiz."
        elif grade.percentage >= 50:
            feedback = "Qoniqarli. Yana biroz harakat qiling!"
        else:
            feedback = "Natija past. Darslarga ko'proq e'tibor qarating!"
        
        message = f"""🏆⭐️ <b>Sizning bahoyingiz yangilandi!</b>

📚 <b>Guruh:</b> {grade.lesson.group.name}
📘 <b>Dars:</b> {grade.lesson.topic or 'Mavzu belgilanmagan'}
📅 <b>Sana:</b> {grade.lesson.lesson_date.strftime('%d.%m.%Y')}

━━━━━━━━━━━━━━━
⭐️ <b>Sizning bahoyingiz:</b> {grade.percentage}%
⭐️ <b>Yulduzli natija:</b> {stars}
⭐️ <b>Fikr:</b> {grade.feedback or feedback}
📝 <b>Izoh:</b> {grade.comment or "Ustoz tomonidan qo'shimcha izoh qoldirilmagan."}

⭐️ Oldinga qarab shunday davom eting!"""
        
        service = get_telegram_service()
        await service.send_message(grade.student.telegram_chat_id, message)
    
    @staticmethod
    async def notify_payment_recorded(db: Session, payment_id: UUID):
        """Notify student when payment is recorded"""
        try:
            from app.models.payment import Payment
            
            payment = db.query(Payment).filter(
                Payment.id == payment_id
            ).first()
            
            if not payment:
                return
            
            title = "💰 Payment Recorded"
            message = f"""
Amount: ${payment.amount:,.2f}
Month: {payment.payment_month}
Type: {payment.type.value.upper()}
Group: {payment.group.name if payment.group else 'General'}
            """
            
            service = get_telegram_service()
            await service.notify_user(
                db, payment.student_id, "payment_recorded", title, message
            )
        except Exception as e:
            logger.error(f"Error in notify_payment_recorded: {e}")