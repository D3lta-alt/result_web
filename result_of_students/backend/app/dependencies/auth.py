"""
app/dependencies/auth.py
"""

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies.db import get_db
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

# ── Role hierarchy: higher index = more access ────────
ROLE_LEVEL: dict[UserRole, int] = {
    UserRole.viewer: 0,
    UserRole.staff:  1,
    UserRole.admin:  2,
}

_bearer = HTTPBearer(auto_error=True)
_bearer_optional = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _decode_token(token: str) -> TokenPayload:
    """Decode and validate a JWT; raise 401 on any failure."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return TokenPayload(**payload)
    except (JWTError, Exception):
        raise _CREDENTIALS_EXCEPTION


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode the Bearer JWT and return the matching active User.
    Raises 401 if token is invalid or user is inactive/deleted.
    """
    payload = _decode_token(credentials.credentials)

    if payload.type != "access":
        raise _CREDENTIALS_EXCEPTION

    result = await db.execute(select(User).where(User.id == int(payload.sub)))
    user: User | None = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise _CREDENTIALS_EXCEPTION

    return user


async def optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Same as get_current_user but returns None when no token is provided."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)  # type: ignore[arg-type]
    except HTTPException:
        return None


def require_role(*roles: UserRole) -> Callable:
    """
    Dependency factory.

        @router.delete("/{id}", dependencies=[Depends(require_role(UserRole.admin))])

    Pass a single role for minimum-level check:
        require_role(UserRole.staff)  →  staff OR admin passes
    """
    min_level = min(ROLE_LEVEL[r] for r in roles)

    async def _check(user: User = Depends(get_current_user)) -> User:
        if ROLE_LEVEL[user.role] < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action.",
            )
        return user

    return _check