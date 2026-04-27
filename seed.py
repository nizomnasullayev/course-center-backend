"""
Minimal database seeding script (Alembic-safe: no create_all / drop_all).

Creates:
- 2 superadmins (platform-level; course_center_id is NULL)
- 2 course centers
- 2 admins (one per course center)
"""

import sys

from sqlalchemy import text, bindparam

sys.path.append(".")

from app.database import SessionLocal
from app.models.course_center import CourseCenter
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def clear_database(db) -> None:
    """
    Clear data only. Requires Postgres (uses TRUNCATE).
    """
    wanted = [
        "notification_logs",
        "grades",
        "attendance",
        "payments",
        "lessons",
        "group_students",
        "groups",
        "subjects",
        "users",
        "course_centers",
    ]

    stmt = text(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name IN :names
        """
    ).bindparams(bindparam("names", expanding=True))

    existing = db.execute(stmt, {"names": wanted}).scalars().all()

    # Keep the truncation order stable and safe.
    ordered = [name for name in wanted if name in set(existing)]
    if not ordered:
        return

    truncate_sql = "TRUNCATE TABLE " + ", ".join(ordered) + " RESTART IDENTITY CASCADE;"
    db.execute(text(truncate_sql))
    db.commit()


def seed_database(clear: bool = True) -> None:
    db = SessionLocal()
    try:
        if clear:
            clear_database(db)

        # Superadmins (no course_center_id)
        superadmin1 = User(
            full_name="Super Admin 1",
            email="superadmin1@course-center.local",
            phone_number="+998900000001",
            password=get_password_hash("superadmin123"),
            role=UserRole.SUPER_ADMIN,
            status=True,
        )
        superadmin2 = User(
            full_name="Super Admin 2",
            email="superadmin2@course-center.local",
            phone_number="+998900000002",
            password=get_password_hash("superadmin123"),
            role=UserRole.SUPER_ADMIN,
            status=True,
        )
        db.add_all([superadmin1, superadmin2])
        db.flush()

        # Course centers (match app/models/course_center.py fields)
        cc1 = CourseCenter(
            name="Course Center 1",
            address="Tashkent",
            phone_number="+998900001001",
            status=True,
        )
        cc2 = CourseCenter(
            name="Course Center 2",
            address="Samarkand",
            phone_number="+998900001002",
            status=True,
        )
        db.add_all([cc1, cc2])
        db.flush()

        # Admins (tenant-scoped)
        admin1 = User(
            full_name="Admin 1",
            email="admin1@course-center.local",
            phone_number="+998900000101",
            password=get_password_hash("admin12345"),
            role=UserRole.ADMIN,
            status=True,
            course_center_id=cc1.id,
        )
        admin2 = User(
            full_name="Admin 2",
            email="admin2@course-center.local",
            phone_number="+998900000102",
            password=get_password_hash("admin12345"),
            role=UserRole.ADMIN,
            status=True,
            course_center_id=cc2.id,
        )
        db.add_all([admin1, admin2])

        db.commit()

        print("Seed completed.")
        print("Superadmin1: superadmin1@course-center.local / superadmin123")
        print("Superadmin2: superadmin2@course-center.local / superadmin123")
        print("Admin1: admin1@course-center.local / admin12345 (Course Center 1)")
        print("Admin2: admin2@course-center.local / admin12345 (Course Center 2)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()