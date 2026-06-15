"""
app/schemas/grade.py
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class GradeCreate(BaseModel):
    subject_id: int
    grade_point: Decimal
    grade_letter: str
    final_grade: str
    remarks: str | None = None

    @field_validator("grade_point")
    @classmethod
    def validate_grade_point(cls, v: Decimal) -> Decimal:
        if not (0 <= v <= 4):
            raise ValueError("grade_point must be between 0.00 and 4.00")
        return v

    @field_validator("final_grade")
    @classmethod
    def validate_final_grade(cls, v: str) -> str:
        allowed = {"PASS", "FAIL", "ABS", "W"}
        if v.upper() not in allowed:
            raise ValueError(f"final_grade must be one of {allowed}")
        return v.upper()


class GradeUpdate(BaseModel):
    grade_point: Decimal | None = None
    grade_letter: str | None = None
    final_grade: str | None = None
    remarks: str | None = None


class GradeOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    student_id: int
    subject_id: int
    grade_point: Decimal
    grade_letter: str
    final_grade: str
    remarks: str | None
    created_at: datetime


class GradeWithSubject(GradeOut):
    """Grade response that includes subject details — used in marksheet."""
    subject_code: str = ""
    subject_name: str = ""
    credit_hours: int = 0