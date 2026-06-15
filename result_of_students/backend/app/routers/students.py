"""
app/routers/students.py
GET /students        — viewer+  (search + pagination)
GET /students/{id}   — viewer+  (full record with grades)
POST/PATCH           — staff+
DELETE               — admin only
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_role
from app.dependencies.db import get_db
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate, StudentWithGrades
from app.services import grade_service, student_service

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=dict)
async def search_students(
    name: str | None = Query(None, description="Partial student name (case-insensitive)"),
    dob: str | None = Query(None, description="Date of birth in B.S. (DD/MM/YYYY)"),
    passing_year: int | None = Query(None, description="Passing year in B.S."),
    institute_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    skip = (page - 1) * page_size
    students, total = await student_service.search_students(
        db,
        name=name,
        dob=dob,
        passing_year=passing_year,
        institute_id=institute_id,
        skip=skip,
        limit=page_size,
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "results": [StudentOut.model_validate(s) for s in students],
    }


@router.post(
    "/",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.staff))],
)
async def create_student(body: StudentCreate, db: AsyncSession = Depends(get_db)):
    student = await student_service.create_student(db, body)
    return StudentOut.model_validate(student)


@router.get("/{student_id}", response_model=StudentWithGrades)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return full student record with all grades (used for the marksheet)."""
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    enriched_grades = await grade_service.get_grades_for_student(db, student_id)

    out = StudentWithGrades.model_validate(student)
    out.grades = enriched_grades   # type: ignore[assignment]
    return out


@router.patch(
    "/{student_id}",
    response_model=StudentOut,
    dependencies=[Depends(require_role(UserRole.staff))],
)
async def update_student(
    student_id: int, body: StudentUpdate, db: AsyncSession = Depends(get_db)
):
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    updated = await student_service.update_student(db, student, body)
    return StudentOut.model_validate(updated)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.admin))],
)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    await student_service.delete_student(db, student)
    return None