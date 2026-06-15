"""
app/models/student.py
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # B.S. dates stored as strings (e.g. "04/07/2056 B.S.")
    dob_bs: Mapped[str | None] = mapped_column(String(20))
    # A.D. date stored as string for display (converted from BS)
    dob_ad: Mapped[str | None] = mapped_column(String(20))

    reg_no: Mapped[str | None] = mapped_column(String(50), index=True)
    symbol_no: Mapped[str | None] = mapped_column(String(50), index=True)

    passing_year_bs: Mapped[int | None] = mapped_column(Integer, index=True)
    major: Mapped[str | None] = mapped_column(String(100))

    institute_id: Mapped[int] = mapped_column(
        ForeignKey("institutes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
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
    institute: Mapped["Institute"] = relationship(
        back_populates="students", lazy="select"
    )
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Student id={self.id} name={self.full_name!r}>"