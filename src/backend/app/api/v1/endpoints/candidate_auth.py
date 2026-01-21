"""
Candidate Authentication API Endpoints
Authentication for job portal candidates (separate from internal employees)
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4
import secrets
import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from jose import jwt, JWTError
import bcrypt

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

# JWT settings
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 scheme for candidate tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/candidates/auth/login", auto_error=False)


# ============================================================================
# Request/Response Models
# ============================================================================

class CandidateRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class CandidateLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    message: str


class CandidateUserResponse(BaseModel):
    id: UUID
    email: str


# ============================================================================
# Helper Functions
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


async def get_current_candidate(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Dependency to get the current authenticated candidate."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Get candidate user from database
    result = await db.execute(
        select_candidate_user_by_id(UUID(user_id))
    )
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "candidate_id": str(user.candidate_id) if hasattr(user, 'candidate_id') and user.candidate_id else None
    }


def select_candidate_user_by_id(user_id: UUID):
    """Build select query for candidate user by ID."""
    from sqlalchemy import text
    return text("""
        SELECT id, email, password_hash, email_verified, is_active, candidate_id
        FROM candidate_users
        LEFT JOIN candidate_profiles ON candidate_users.id = candidate_profiles.user_id
        WHERE candidate_users.id = :user_id
    """).bindparams(user_id=user_id)


def select_candidate_user_by_email(email: str):
    """Build select query for candidate user by email."""
    from sqlalchemy import text
    return text("""
        SELECT id, email, password_hash, email_verified, is_active
        FROM candidate_users
        WHERE email = :email
    """).bindparams(email=email)


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/register", response_model=TokenResponse)
async def register_candidate(
    request: CandidateRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new candidate account."""
    from sqlalchemy import text

    # Check if email already exists
    result = await db.execute(
        text("SELECT id FROM candidate_users WHERE email = :email").bindparams(email=request.email)
    )
    existing_user = result.first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create candidate user
    user_id = uuid4()
    password_hash = get_password_hash(request.password)
    verification_token = generate_verification_token()

    await db.execute(
        text("""
            INSERT INTO candidate_users (id, email, password_hash, verification_token, created_at, updated_at)
            VALUES (:id, :email, :password_hash, :verification_token, NOW(), NOW())
        """).bindparams(
            id=user_id,
            email=request.email,
            password_hash=password_hash,
            verification_token=verification_token
        )
    )

    # Create candidate profile (without linking to candidates table yet)
    # The candidate record in the candidates table will be created when they apply for a job
    profile_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO candidate_profiles (id, user_id, candidate_id, headline, created_at, updated_at)
            VALUES (:id, :user_id, NULL, :headline, NOW(), NOW())
        """).bindparams(
            id=profile_id,
            user_id=user_id,
            headline=f"{request.first_name} {request.last_name}"
        )
    )

    await db.commit()

    # Generate tokens
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    # TODO: Send verification email
    # await send_verification_email(request.email, verification_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user_id),
            "email": request.email
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login_candidate(
    request: CandidateLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with candidate credentials."""
    from sqlalchemy import text

    # Get user by email
    result = await db.execute(
        text("""
            SELECT id, email, password_hash, email_verified, is_active
            FROM candidate_users
            WHERE email = :email
        """).bindparams(email=request.email)
    )
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )

    # Update last login
    await db.execute(
        text("UPDATE candidate_users SET last_login_at = NOW() WHERE id = :id").bindparams(id=user.id)
    )
    await db.commit()

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    from sqlalchemy import text

    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Verify user exists
    result = await db.execute(
        text("SELECT id, email, is_active FROM candidate_users WHERE id = :id").bindparams(id=UUID(user_id))
    )
    user = result.first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user={
            "id": str(user.id),
            "email": user.email
        }
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify email address using token."""
    from sqlalchemy import text

    result = await db.execute(
        text("""
            SELECT id, email FROM candidate_users
            WHERE verification_token = :token AND email_verified = FALSE
        """).bindparams(token=request.token)
    )
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    await db.execute(
        text("""
            UPDATE candidate_users
            SET email_verified = TRUE, email_verified_at = NOW(), verification_token = NULL
            WHERE id = :id
        """).bindparams(id=user.id)
    )
    await db.commit()

    return MessageResponse(message="Email verified successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset email."""
    from sqlalchemy import text

    result = await db.execute(
        text("SELECT id, email FROM candidate_users WHERE email = :email").bindparams(email=request.email)
    )
    user = result.first()

    # Always return success to prevent email enumeration
    if user:
        reset_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)

        await db.execute(
            text("""
                UPDATE candidate_users
                SET reset_token = :token, reset_token_expires_at = :expires_at
                WHERE id = :id
            """).bindparams(token=reset_token, expires_at=expires_at, id=user.id)
        )
        await db.commit()

        # TODO: Send password reset email
        # await send_password_reset_email(user.email, reset_token)

    return MessageResponse(message="If an account exists with this email, you will receive a password reset link")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using token."""
    from sqlalchemy import text

    result = await db.execute(
        text("""
            SELECT id FROM candidate_users
            WHERE reset_token = :token
            AND reset_token_expires_at > NOW()
        """).bindparams(token=request.token)
    )
    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    password_hash = get_password_hash(request.password)

    await db.execute(
        text("""
            UPDATE candidate_users
            SET password_hash = :password_hash, reset_token = NULL, reset_token_expires_at = NULL
            WHERE id = :id
        """).bindparams(password_hash=password_hash, id=user.id)
    )
    await db.commit()

    return MessageResponse(message="Password reset successfully")
