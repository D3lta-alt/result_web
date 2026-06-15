"""
app/services/grade_service.py
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.grade import Grade
from app.models.subject import Subject
from app.schemas.grade import GradeCreate, GradeWithSubject


async def get_grades_for_student(
    db: AsyncSession, student_id: int
) -> list[GradeWithSubject]:
    """
    Return all grades for a student, each enriched with subject info.
    """
    result = await db.execute(
        select(Grade)
        .options(selectinload(Grade.subject))
        .where(Grade.student_id == student_id)
        .order_by(Grade.subject_id)
    )
    grades = result.scalars().all()

    enriched: list[GradeWithSubject] = []
    for g in grades:
        out = GradeWithSubject.model_validate(g)
        if g.subject:
            out.subject_code = g.subject.code
            out.subject_name = g.subject.name
            out.credit_hours = g.subject.credit_hours
        enriched.append(out)

    return enriched


async def upsert_grades(
    db: AsyncSession,
    student_id: int,
    grades_data: list[GradeCreate],
) -> list[Grade]:
    """
    Insert or update grades for a student.
    Uses INSERT ... ON CONFLICT (student_id, subject_id) DO UPDATE.
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    result_grades: list[Grade] = []

    for g in grades_data:
        stmt = (
            pg_insert(Grade)
            .values(
                student_id=student_id,
                subject_id=g.subject_id,
                grade_point=g.grade_point,
                grade_letter=g.grade_letter,
                final_grade=g.final_grade,
                remarks=g.remarks,
            )
            .on_conflict_do_update(
                constraint="uq_student_subject",
                set_=dict(
                    grade_point=g.grade_point,
                    grade_letter=g.grade_letter,
                    final_grade=g.final_grade,
                    remarks=g.remarks,
                ),
            )
            .returning(Grade)
        )
        r = await db.execute(stmt)
        result_grades.append(r.scalar_one())

    await db.flush()
    return result_grades