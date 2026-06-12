"""Initial schema — institutes, users, students, subjects, grades

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── institutes ────────────────────────────────────
    op.create_table(
        "institutes",
        sa.Column("id",          sa.Integer(),     primary_key=True),
        sa.Column("name",        sa.String(200),   nullable=False),
        sa.Column("address",     sa.String(300),   nullable=True),
        sa.Column("phone",       sa.String(30),    nullable=True),
        sa.Column("email",       sa.String(150),   nullable=True),
        sa.Column("description", sa.Text(),        nullable=True),
        sa.Column("is_active",   sa.Boolean(),     nullable=False, server_default="true"),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_institutes_id",   "institutes", ["id"],   unique=False)
    op.create_index("ix_institutes_name", "institutes", ["name"], unique=True)

    # ── userrole enum ─────────────────────────────────
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'staff', 'viewer')")

    # ── users ─────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",              sa.Integer(),   primary_key=True),
        sa.Column("email",           sa.String(150), nullable=False),
        sa.Column("full_name",       sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role",            sa.Text(),      nullable=False, server_default="viewer"),
        sa.Column("is_active",       sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("institute_id",    sa.Integer(),   sa.ForeignKey("institutes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_id",           "users", ["id"],           unique=False)
    op.create_index("ix_users_email",        "users", ["email"],        unique=True)
    op.create_index("ix_users_institute_id", "users", ["institute_id"], unique=False)

    # ── students ──────────────────────────────────────
    op.create_table(
        "students",
        sa.Column("id",              sa.Integer(),   primary_key=True),
        sa.Column("full_name",       sa.String(200), nullable=False),
        sa.Column("dob_bs",          sa.String(20),  nullable=True),
        sa.Column("dob_ad",          sa.String(20),  nullable=True),
        sa.Column("reg_no",          sa.String(50),  nullable=True),
        sa.Column("symbol_no",       sa.String(50),  nullable=True),
        sa.Column("passing_year_bs", sa.Integer(),   nullable=True),
        sa.Column("major",           sa.String(100), nullable=True),
        sa.Column("institute_id",    sa.Integer(),   sa.ForeignKey("institutes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_students_id",              "students", ["id"],              unique=False)
    op.create_index("ix_students_full_name",       "students", ["full_name"],       unique=False)
    op.create_index("ix_students_reg_no",          "students", ["reg_no"],          unique=False)
    op.create_index("ix_students_symbol_no",       "students", ["symbol_no"],       unique=False)
    op.create_index("ix_students_passing_year_bs", "students", ["passing_year_bs"], unique=False)
    op.create_index("ix_students_institute_id",    "students", ["institute_id"],    unique=False)

    # ── subjects ──────────────────────────────────────
    op.create_table(
        "subjects",
        sa.Column("id",           sa.Integer(),   primary_key=True),
        sa.Column("code",         sa.String(20),  nullable=False),
        sa.Column("name",         sa.String(200), nullable=False),
        sa.Column("credit_hours", sa.Integer(),   nullable=False, server_default="3"),
        sa.Column("institute_id", sa.Integer(),   sa.ForeignKey("institutes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_subjects_id",           "subjects", ["id"],           unique=False)
    op.create_index("ix_subjects_code",         "subjects", ["code"],         unique=False)
    op.create_index("ix_subjects_institute_id", "subjects", ["institute_id"], unique=False)

    # ── grades ────────────────────────────────────────
    op.create_table(
        "grades",
        sa.Column("id",           sa.Integer(),     primary_key=True),
        sa.Column("student_id",   sa.Integer(),     sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id",   sa.Integer(),     sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grade_point",  sa.Numeric(4, 2), nullable=False),
        sa.Column("grade_letter", sa.String(5),     nullable=False),
        sa.Column("final_grade",  sa.String(10),    nullable=False),
        sa.Column("remarks",      sa.Text(),        nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",   sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )
    op.create_index("ix_grades_id",         "grades", ["id"],         unique=False)
    op.create_index("ix_grades_student_id", "grades", ["student_id"], unique=False)
    op.create_index("ix_grades_subject_id", "grades", ["subject_id"], unique=False)


def downgrade() -> None:
    op.drop_table("grades")
    op.drop_table("subjects")
    op.drop_table("students")
    op.drop_table("users")
    op.drop_table("institutes")
    op.execute("DROP TYPE userrole")