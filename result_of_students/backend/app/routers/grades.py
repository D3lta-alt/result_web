"""
app/routers/grades.py
GET  /students/{id}/grades  — viewer+
POST /students/{id}/grades  — staff+ (upsert bulk)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_role
from app.dependencies.db import get_db
from app.models.user import User, UserRole
from app.schemas.grade import GradeCreate, GradeWithSubject
from app.services import grade_service, student_service

router = APIRouter(tags=["Grades"])


@router.get(
    "/students/{student_id}/grades",
    response_model=list[GradeWithSubject],
)
async def get_grades(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    return await grade_service.get_grades_for_student(db, student_id)


@router.post(
    "/students/{student_id}/grades",
    response_model=list[GradeWithSubject],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.staff))],
)
async def upsert_grades(
    student_id: int,
    grades: list[GradeCreate],
    db: AsyncSession = Depends(get_db),
):
    if not grades:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="grades list cannot be empty.",
        )

    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    await grade_service.upsert_grades(db, student_id, grades)
    return await grade_service.get_grades_for_student(db, student_id)