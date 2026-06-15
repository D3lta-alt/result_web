"""
app/main.py
FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.routers import auth, grades, institutes, students, users


# ── Lifespan ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup/shutdown logic around the app lifecycle."""
    # Nothing to init at startup (SQLAlchemy pool is lazy)
    yield
    # On shutdown: dispose connection pool cleanly
    from app.database import engine
    await engine.dispose()


# ── App ───────────────────────────────────────────────
app = FastAPI(
    title="Academia API",
    description="Student search and grade management backend.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )

# ── Routers ───────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(auth.router,       prefix=API_PREFIX)
app.include_router(users.router,      prefix=API_PREFIX)
app.include_router(institutes.router, prefix=API_PREFIX)
app.include_router(students.router,   prefix=API_PREFIX)
app.include_router(grades.router,     prefix=API_PREFIX)


# ── Health check ──────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health():
    """Quick liveness probe — no DB required."""
    return {"status": "ok", "version": app.version}