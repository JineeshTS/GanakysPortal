"""
API Dependencies
Common dependencies used across API endpoints
"""
from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.db.session import get_db
from app.core.config import settings

# Re-export get_db for convenience
__all__ = ["get_db", "get_current_user", "get_current_company", "require_current_user", "oauth2_scheme"]

# auto_error=False allows endpoints to optionally handle unauthenticated requests
# Use require_current_user for endpoints that MUST have authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Get current authenticated user from JWT token.
    Checks both Authorization header and httpOnly cookies.
    Returns None if no token provided or token is invalid.
    """
    # If no token from Authorization header, check cookies
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Import here to avoid circular imports
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_company(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[UUID]:
    """
    Get current company ID from JWT token.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        company_id: str = payload.get("company_id")
        if company_id:
            return UUID(company_id)
        return None
    except JWTError:
        return None


async def require_current_user(
    user = Depends(get_current_user)
):
    """
    Require authenticated user - raises 401 if not authenticated.

    Use this dependency for endpoints that MUST have authentication.
    Unlike get_current_user which returns None for unauthenticated requests,
    this will always raise HTTPException if the user is not authenticated.

    Usage:
        @router.get("/protected")
        async def protected_endpoint(user = Depends(require_current_user)):
            # user is guaranteed to be non-None here
            ...
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
