"""
app/schemas/institute.py
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class InstituteCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    description: str | None = None


class InstituteUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    description: str | None = None
    is_active: bool | None = None


class InstituteOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    address: str | None
    phone: str | None
    email: str | None
    description: str | None
    is_active: bool
    created_at: datetime