"""
alembic/env.py
Alembic migration environment.

Key points:
 - Uses a *sync* psycopg2 URL (Alembic doesn't support asyncpg directly).
 - Imports all models via app.models so autogenerate detects every table.
 - DATABASE_URL is read from .env via app.config.settings.
"""

import re
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.config import settings
from app.database import Base
import app.models  # noqa: F401 — registers all ORM classes with Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """
    Convert asyncpg URL → psycopg2 URL for Alembic.
    postgresql+asyncpg://... → postgresql+psycopg2://...
    """
    url = settings.DATABASE_URL
    return re.sub(r"postgresql\+asyncpg", "postgresql+psycopg2", url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection)."""
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to DB)."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()