"""
app/models/__init__.py
Import all ORM models here so that:
  - Alembic's env.py can do `from app.models import *` and see every table
  - Circular imports are avoided across the codebase
"""

from app.models.institute import Institute          # noqa: F401
from app.models.user import User, UserRole          # noqa: F401
from app.models.student import Student              # noqa: F401
from app.models.subject import Subject              # noqa: F401
from app.models.grade import Grade                  # noqa: F401