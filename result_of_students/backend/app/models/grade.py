"""
app/models/grade.py
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        # One grade entry per student per subject
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    grade_point: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    grade_letter: Mapped[str] = mapped_column(String(5), nullable=False)
    final_grade: Mapped[str] = mapped_column(String(10), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────
    student: Mapped["Student"] = relationship(
        back_populates="grades", lazy="select"
    )
    subject: Mapped["Subject"] = relationship(
        back_populates="grades", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<Grade student={self.student_id} "
            f"subject={self.subject_id} gp={self.grade_point}>"
        )