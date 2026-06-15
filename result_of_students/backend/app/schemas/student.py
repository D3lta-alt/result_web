"""
app/schemas/student.py
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StudentCreate(BaseModel):
    full_name: str
    dob_bs: str | None = None
    dob_ad: str | None = None
    reg_no: str | None = None
    symbol_no: str | None = None
    passing_year_bs: int | None = None
    major: str | None = None
    institute_id: int


class StudentUpdate(BaseModel):
    full_name: str | None = None
    dob_bs: str | None = None
    dob_ad: str | None = None
    reg_no: str | None = None
    symbol_no: str | None = None
    passing_year_bs: int | None = None
    major: str | None = None
    institute_id: int | None = None


class StudentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    full_name: str
    dob_bs: str | None
    dob_ad: str | None
    reg_no: str | None
    symbol_no: str | None
    passing_year_bs: int | None
    major: str | None
    institute_id: int
    created_at: datetime


class StudentWithGrades(StudentOut):
    """Extended response that includes grades — used for marksheet."""
    grades: list = []