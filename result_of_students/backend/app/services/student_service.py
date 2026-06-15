"""
app/services/student_service.py
All database logic for students so routers stay thin.
"""

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


async def get_student_by_id(db: AsyncSession, student_id: int) -> Student | None:
    """Fetch a student with all grades + subjects eagerly loaded."""
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.grades))
        .where(Student.id == student_id)
    )
    return result.scalar_one_or_none()


async def search_students(
    db: AsyncSession,
    *,
    name: str | None = None,
    dob: str | None = None,
    passing_year: int | None = None,
    institute_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Student], int]:
    """
    Search students with optional filters.
    Returns (students, total_count).
    """
    conditions = []

    if name:
        conditions.append(
            func.upper(Student.full_name).contains(name.upper())
        )
    if dob:
        conditions.append(Student.dob_bs == dob)
    if passing_year:
        conditions.append(Student.passing_year_bs == passing_year)
    if institute_id:
        conditions.append(Student.institute_id == institute_id)

    where_clause = and_(*conditions) if conditions else True

    # Total count (for pagination)
    count_result = await db.execute(
        select(func.count(Student.id)).where(where_clause)
    )
    total = count_result.scalar_one()

    # Paginated rows
    rows_result = await db.execute(
        select(Student)
        .where(where_clause)
        .order_by(Student.full_name)
        .offset(skip)
        .limit(limit)
    )
    students = list(rows_result.scalars().all())

    return students, total


async def create_student(db: AsyncSession, data: StudentCreate) -> Student:
    student = Student(**data.model_dump())
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return student


async def update_student(
    db: AsyncSession, student: Student, data: StudentUpdate
) -> Student:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.flush()
    await db.refresh(student)
    return student


async def delete_student(db: AsyncSession, student: Student) -> None:
    await db.delete(student)
    await db.flush()