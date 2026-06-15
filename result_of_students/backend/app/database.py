"""
app/database.py
Async SQLAlchemy 2.0 engine + session factory.
All models import `Base` from here so Alembic can discover them.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Shared declarative base — import in every model file."""
    pass


# ── Engine ────────────────────────────────────────────
# pool_pre_ping=True — drops stale connections automatically
# echo only in dev so SQL isn't logged in production
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.is_development,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory ───────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # objects remain usable after commit
    autoflush=False,
    autocommit=False,
)