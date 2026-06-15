"""
app/routers/institutes.py
GET — all roles; POST/PATCH/DELETE — admin only.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_role
from app.dependencies.db import get_db
from app.models.institute import Institute
from app.models.user import User, UserRole
from app.schemas.institute import InstituteCreate, InstituteOut, InstituteUpdate

router = APIRouter(prefix="/institutes", tags=["Institutes"])


@router.get("/", response_model=list[InstituteOut])
async def list_institutes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Institute)
        .where(Institute.is_active == True)      # noqa: E712
        .order_by(Institute.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post(
    "/",
    response_model=InstituteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.admin))],
)
async def create_institute(body: InstituteCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Institute).where(Institute.name == body.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An institute with this name already exists.",
        )
    institute = Institute(**body.model_dump())
    db.add(institute)
    await db.flush()
    await db.refresh(institute)
    return institute


@router.get("/{institute_id}", response_model=InstituteOut)
async def get_institute(
    institute_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Institute).where(Institute.id == institute_id)
    )
    institute = result.scalar_one_or_none()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found.")
    return institute


@router.patch(
    "/{institute_id}",
    response_model=InstituteOut,
    dependencies=[Depends(require_role(UserRole.admin))],
)
async def update_institute(
    institute_id: int, body: InstituteUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Institute).where(Institute.id == institute_id)
    )
    institute: Institute | None = result.scalar_one_or_none()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(institute, field, value)

    await db.flush()
    await db.refresh(institute)
    return institute


@router.delete(
    "/{institute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.admin))],
)
async def delete_institute(institute_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Institute).where(Institute.id == institute_id)
    )
    institute: Institute | None = result.scalar_one_or_none()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found.")
    await db.delete(institute)
    await db.flush()
    return None