"""
Authentication Endpoints
Login, logout, token refresh, password management
"""
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
import redis.asyncio as redis
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserSession, AuditLog

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# Redis connection for token blacklist and password reset tokens
redis_client = None

async def get_redis():
    """Get Redis client for token management."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


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
    """Verify password against hash (supports bcrypt and PBKDF2)."""
    if not plain_password or not hashed_password:
        return False

    # Try bcrypt format first (starts with $2)
    if hashed_password.startswith('$2'):
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    # Try PBKDF2 format (salt$hash)
    if '$' in hashed_password:
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

    return False


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


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


async def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    try:
        r = await get_redis()
        return await r.exists(f"blacklist:{token}") > 0
    except Exception:
        return False


async def blacklist_token(token: str, expires_in: int):
    """Add token to blacklist."""
    try:
        r = await get_redis()
        await r.setex(f"blacklist:{token}", expires_in, "1")
    except Exception:
        pass


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

    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise credentials_exception

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


async def log_audit(
    db: AsyncSession,
    user_id: str | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    old_values: str | None = None,
    new_values: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None
):
    """Log an audit event."""
    try:
        from uuid import UUID
        audit = AuditLog(
            user_id=UUID(user_id) if user_id else None,
            action=action,
            entity_type=entity_type,
            entity_id=UUID(entity_id) if entity_id else None,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        await db.commit()
    except Exception:
        pass


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email using Hostinger SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg["To"] = to_email

        msg.attach(MIMEText(html_body, "html"))

        # Use SSL for port 465
        if settings.SMTP_USE_SSL:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        else:
            # Use TLS for port 587
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


# Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
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

    # Check if user exists
    if not user:
        await log_audit(db, None, "login_failed", "user", None, None,
                       f'{{"email": "{form_data.username}", "reason": "user_not_found"}}',
                       request.client.host if request.client else None,
                       request.headers.get("user-agent"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked. Try again after {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)

        await db.commit()

        await log_audit(db, str(user.id), "login_failed", "user", str(user.id), None,
                       f'{{"reason": "invalid_password", "attempts": {user.failed_login_attempts}}}',
                       request.client.host if request.client else None,
                       request.headers.get("user-agent"))

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

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None

    # Build user response
    user_data = {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
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

    # Log successful login
    await log_audit(db, str(user.id), "login_success", "user", str(user.id), None, None,
                   request.client.host if request.client else None,
                   request.headers.get("user-agent"))

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    # Check if refresh token is blacklisted
    if await is_token_blacklisted(request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

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

        # Blacklist old refresh token
        exp = payload.get("exp", 0)
        remaining = max(0, exp - int(datetime.utcnow().timestamp()))
        await blacklist_token(request.refresh_token, remaining)

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
    request: Request,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate tokens."""
    # Get the token from the request
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Blacklist for remaining token lifetime (15 minutes max for access token)
        await blacklist_token(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    # Log logout
    await log_audit(db, current_user.user_id, "logout", "user", current_user.user_id,
                   None, None,
                   request.client.host if request.client else None,
                   request.headers.get("user-agent"))

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's profile."""
    # Fetch actual user from database
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(current_user.user_id)))
    user = result.scalar_one_or_none()

    if user:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value if hasattr(user.role, 'value') else str(user.role),
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
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Change password for authenticated user."""
    from uuid import UUID

    # Get user from database
    result = await db.execute(select(User).where(User.id == UUID(current_user.user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        await log_audit(db, current_user.user_id, "password_change_failed", "user",
                       current_user.user_id, None, '{"reason": "invalid_current_password"}',
                       request.client.host if request.client else None,
                       request.headers.get("user-agent"))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )

    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    user.password_changed_at = datetime.utcnow()
    await db.commit()

    # Log password change
    await log_audit(db, current_user.user_id, "password_changed", "user",
                   current_user.user_id, None, None,
                   request.client.host if request.client else None,
                   request.headers.get("user-agent"))

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset email."""
    # Always return success to prevent email enumeration
    response_message = "If the email exists, a reset link has been sent"

    # Look up user
    result = await db.execute(select(User).where(User.email == forgot_data.email))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # Store in Redis with expiration
        try:
            r = await get_redis()
            await r.setex(
                f"password_reset:{reset_token}",
                settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS * 3600,
                str(user.id)
            )
        except Exception as e:
            print(f"Redis error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not process request"
            )

        # Send email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Password Reset Request</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password for your GanaPortal account.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background-color: #2563eb; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666; font-size: 14px;">{reset_url}</p>
                <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.</p>
                <p>If you did not request a password reset, please ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #666; font-size: 12px;">
                    This email was sent by GanaPortal. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """

        email_sent = send_email(user.email, "Password Reset - GanaPortal", html_body)

        if email_sent:
            await log_audit(db, str(user.id), "password_reset_requested", "user",
                           str(user.id), None, None,
                           request.client.host if request.client else None,
                           request.headers.get("user-agent"))

    return {"message": response_message}


@router.post("/reset-password")
async def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using token from email."""
    from uuid import UUID

    # Validate token
    try:
        r = await get_redis()
        user_id = await r.get(f"password_reset:{reset_data.token}")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process request"
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Validate new password
    if len(reset_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Get user and update password
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    # Delete used token
    try:
        await r.delete(f"password_reset:{reset_data.token}")
    except Exception:
        pass

    # Log password reset
    await log_audit(db, str(user.id), "password_reset_completed", "user",
                   str(user.id), None, None,
                   request.client.host if request.client else None,
                   request.headers.get("user-agent"))

    # Send confirmation email
    html_body = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Password Changed Successfully</h2>
            <p>Hello,</p>
            <p>Your GanaPortal password has been successfully changed.</p>
            <p>If you did not make this change, please contact support immediately.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This email was sent by GanaPortal. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    send_email(user.email, "Password Changed - GanaPortal", html_body)

    return {"message": "Password reset successfully"}
