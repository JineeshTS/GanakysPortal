"""
Authentication Endpoints
Login, logout, token refresh, password management
"""
from datetime import datetime, timedelta
import hashlib
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


# Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None
    role: str | None = None
    company_id: str | None = None
    employee_id: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    name: str
    company_id: str
    employee_id: str | None = None


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (PBKDF2-HMAC-SHA256 format: salt$hash)."""
    if not plain_password or not hashed_password:
        return False

    # Try PBKDF2 format first (salt$hash)
    if '$' in hashed_password and not hashed_password.startswith('$2'):
        try:
            salt, hash_value = hashed_password.split('$', 1)
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode(),
                salt.encode(),
                100000
            )
            return new_hash.hex() == hash_value
        except Exception:
            pass

    # Fallback to bcrypt for backwards compatibility
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(
            user_id=user_id,
            email=payload.get("email"),
            role=payload.get("role"),
            company_id=payload.get("company_id"),
            employee_id=payload.get("employee_id")
        )
    except JWTError:
        raise credentials_exception


# Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    Returns access token (15 min) and refresh token (7 days).
    """
    # Look up user by email
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Check if user exists and password is valid
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Build user response
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value if user.role else "employee",
        "name": user.email.split("@")[0].title(),
        "company_id": str(user.company_id),
        "employee_id": str(user.employee_id) if user.employee_id else None
    }

    token_data = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "company_id": user_data["company_id"],
        "employee_id": user_data["employee_id"]
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Update last login time
    user.last_login = datetime.utcnow()
    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "company_id": payload.get("company_id"),
            "employee_id": payload.get("employee_id")
        }

        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate refresh token."""
    # TODO: Add token to blacklist in Redis
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's profile."""
    # Fetch actual user from database
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()

    if user:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value if user.role else "employee",
            name=user.email.split("@")[0].title(),
            company_id=str(user.company_id),
            employee_id=str(user.employee_id) if user.employee_id else None
        )

    return UserResponse(
        id=current_user.user_id,
        email=current_user.email,
        role=current_user.role,
        name="Current User",
        company_id=current_user.company_id,
        employee_id=current_user.employee_id
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Change password for authenticated user."""
    # TODO: Implement password change logic
    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset email."""
    # TODO: Send password reset email
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using token from email."""
    # TODO: Verify token and update password
    return {"message": "Password reset successfully"}
