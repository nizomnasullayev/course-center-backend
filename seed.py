"""
Database seeding script for Education Management System
Alembic-safe version (NO create_all / drop_all)
"""
import sys
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import text

# Add app to path for imports
sys.path.append('.')

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.group import Group, GroupStatus
from app.models.group_student import GroupStudent
from app.models.lesson import Lesson, LessonStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.payment import Payment, PaymentType

fake = Faker()


# ✅ FIXED: only clear DATA, not schema
def clear_database(db):
    print("🗑️  Clearing existing data...")

    db.execute(text("""
        TRUNCATE TABLE 
            attendance,
            payments,
            lessons,
            group_students,
            groups,
            users,
            subjects,
            course_centers
        RESTART IDENTITY CASCADE;
    """))

    db.commit()
    print("✅ Data cleared")


from app.models.course_center import CourseCenter


def create_initial_data(db):
    print("🏢 Creating Course Center...")
    center = CourseCenter(
        name="Tashkent Main Branch",
        address="Tashkent, Uzbekistan",
        phone_number="+998710000000",
        status=True
    )
    db.add(center)
    db.commit()
    db.refresh(center)

    print("👑 Creating Super Admin...")
    super_admin = User(
        full_name="Super Admin",
        email="superadmin@education.uz",
        phone_number="+998900000000",
        password="superpasswordhash", # Use actual hash in real life
        role=UserRole.SUPER_ADMIN,
        status=True
    )
    db.add(super_admin)
    db.commit()
    
    return center


def create_users(db, center, num_admins=2, num_teachers=5, num_students=30):
    print(f"\n👥 Creating users for {center.name}...")
    users = {"admins": [], "teachers": [], "students": []}

    for i in range(num_admins):
        admin = User(
            full_name=fake.name(),
            email=f"admin{i+1}@education.uz",
            phone_number=f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}",
            password="hashed_password_here",
            role=UserRole.ADMIN,
            course_center_id=center.id,
            status=True
        )
        db.add(admin)
        users["admins"].append(admin)

    for i in range(num_teachers):
        teacher = User(
            full_name=fake.name(),
            email=f"teacher{i+1}@education.uz",
            phone_number=f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}",
            password="hashed_password_here",
            role=UserRole.TEACHER,
            course_center_id=center.id,
            status=True
        )
        db.add(teacher)
        users["teachers"].append(teacher)

    for i in range(num_students):
        student = User(
            full_name=fake.name(),
            email=f"student{i+1}@education.uz" if random.choice([True, False]) else None,
            phone_number=f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}",
            password="hashed_password_here" if random.choice([True, False]) else None,
            role=UserRole.STUDENT,
            course_center_id=center.id,
            parents_phone=f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}",
            status=random.choice([True, True, True, False])
        )
        db.add(student)
        users["students"].append(student)

    db.commit()
    return users


def create_subjects(db, center):
    print("\n📚 Creating subjects...")

    subject_data = [
        {"name": "Mathematics"},
        {"name": "Physics"},
        {"name": "Chemistry"},
        {"name": "English"},
        {"name": "Russian"},
        {"name": "Computer Science"},
        {"name": "Biology"},
    ]

    subjects = []
    for data in subject_data:
        subject = Subject(**data, course_center_id=center.id)
        db.add(subject)
        subjects.append(subject)

    db.commit()
    return subjects


def create_groups(db, subjects, teachers, center):
    print("\n👨‍🏫 Creating groups...")

    schedules = ["Mon-Wed-Fri 09:00", "Tue-Thu-Sat 14:00", "Mon-Wed-Fri 18:00"]

    groups = []

    for subject in subjects:
        for _ in range(random.randint(2, 3)):
            group = Group(
                name=f"{subject.name} Group",
                price=random.choice([300000, 400000, 500000]),
                schedule=random.choice(schedules),
                start_date=fake.date_time_between(start_date='-1m', end_date='+1m'),
                status=random.choice([GroupStatus.ACTIVE, GroupStatus.FINISHED]),
                subject_id=subject.id,
                teacher_id=random.choice(teachers).id,
                course_center_id=center.id
            )
            db.add(group)
            groups.append(group)

    db.commit()
    return groups


def create_group_students(db, groups, students):
    print("\n🎓 Assigning students...")

    group_students = []
    active_students = [s for s in students if s.status]

    for group in groups:
        for student in random.sample(active_students, min(len(active_students), random.randint(5, 10))):
            gs = GroupStudent(
                group_id=group.id,
                student_id=student.id,
                joined_date=group.start_date
            )
            db.add(gs)
            group_students.append(gs)

    db.commit()
    return group_students


def create_lessons(db, groups, center):
    print("\n📝 Creating lessons...")

    lessons = []

    for group in groups:
        for i in range(10):
            lesson = Lesson(
                group_id=group.id,
                teacher_id=group.teacher_id,
                lesson_date=group.start_date + timedelta(days=i * 2),
                status=random.choice([
                    LessonStatus.COMPLETED,
                    LessonStatus.PENDING
                ]),
                course_center_id=center.id
            )
            db.add(lesson)
            lessons.append(lesson)

    db.commit()
    return lessons


def create_attendance(db, lessons, group_students, center):
    print("\n✔️ Creating attendance...")

    attendance = []

    for lesson in lessons:
        for gs in group_students:
            if gs.group_id == lesson.group_id:
                record = Attendance(
                    lesson_id=lesson.id,
                    student_id=gs.student_id,
                    status=random.choice([
                        AttendanceStatus.PRESENT,
                        AttendanceStatus.ABSENT
                    ]),
                    course_center_id=center.id
                )
                db.add(record)
                attendance.append(record)

    db.commit()
    return attendance


def create_payments(db, groups, group_students, center):
    print("\n💰 Creating payments...")

    payments = []

    for gs in group_students:
        group = next(g for g in groups if g.id == gs.group_id)

        payment = Payment(
            student_id=gs.student_id,
            group_id=group.id,
            amount=group.price,
            payment_month="April 2026",
            type=random.choice([
                PaymentType.CASH,
                PaymentType.CARD
            ]),
            course_center_id=center.id
        )
        db.add(payment)
        payments.append(payment)

    db.commit()
    return payments


def seed_database():
    print("🌱 Seeding database...")

    db = SessionLocal()

    try:
        clear_database(db)

        center = create_initial_data(db)
        users = create_users(db, center, 2, 8, 50)
        subjects = create_subjects(db, center)
        groups = create_groups(db, subjects, users["teachers"], center)
        group_students = create_group_students(db, groups, users["students"])
        lessons = create_lessons(db, groups, center)
        create_attendance(db, lessons, group_students, center)
        create_payments(db, groups, group_students, center)

        print("✅ Seeding completed!")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()