"""
Super Admin Authentication Service
Handles authentication, MFA, and session management for super admins
"""
import secrets
import pyotp
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.superadmin import (
    SuperAdmin, SuperAdminSession, SuperAdminAuditLog,
    PlatformSettings
)
from app.core.config import settings


class SuperAdminAuthService:
    """Service for super admin authentication"""

    JWT_SECRET = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "super-secret-key"
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @classmethod
    def create_access_token(cls, admin_id: UUID, role: str) -> str:
        """Create a JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(admin_id),
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def create_refresh_token(cls, admin_id: UUID) -> str:
        """Create a JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(admin_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> Optional[dict]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, cls.JWT_SECRET, algorithms=[cls.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def generate_mfa_secret() -> str:
        """Generate a new MFA secret"""
        return pyotp.random_base32()

    @staticmethod
    def get_mfa_qr_url(secret: str, email: str, issuer: str = "Ganakys Super Admin") -> str:
        """Generate a QR code URL for MFA setup"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def verify_mfa_code(secret: str, code: str) -> bool:
        """Verify an MFA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 30 second window

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """Generate backup codes for MFA recovery"""
        return [secrets.token_hex(4).upper() for _ in range(count)]

    async def authenticate(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        mfa_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[SuperAdmin], Optional[str], Optional[str]]:
        """
        Authenticate a super admin.
        Returns: (admin, error_message, error_code)
        """
        # Find admin by email
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.email == email)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            return None, "Invalid credentials", "INVALID_CREDENTIALS"

        if not admin.is_active:
            return None, "Account is disabled", "ACCOUNT_DISABLED"

        # Verify password
        if not self.verify_password(password, admin.password_hash):
            # Log failed attempt
            audit = SuperAdminAuditLog(
                admin_id=admin.id,
                action="login.failed",
                action_category="auth",
                extra_data={"reason": "invalid_password"},
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(audit)
            await db.commit()

            return None, "Invalid credentials", "INVALID_CREDENTIALS"

        # Check MFA if enabled
        if admin.mfa_enabled:
            if not mfa_code:
                return None, "MFA code required", "MFA_REQUIRED"

            # Check if it's a backup code
            if admin.mfa_backup_codes and mfa_code.upper() in admin.mfa_backup_codes:
                # Remove used backup code
                admin.mfa_backup_codes = [
                    c for c in admin.mfa_backup_codes if c != mfa_code.upper()
                ]
            elif not self.verify_mfa_code(admin.mfa_secret, mfa_code):
                return None, "Invalid MFA code", "INVALID_MFA"

        # Update last login
        admin.last_login = datetime.utcnow()
        admin.last_login_ip = ip_address

        # Log successful login
        audit = SuperAdminAuditLog(
            admin_id=admin.id,
            action="login.success",
            action_category="auth",
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)

        await db.commit()
        await db.refresh(admin)

        return admin, None, None

    async def create_session(
        self,
        db: AsyncSession,
        admin_id: UUID,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Create access and refresh tokens for an admin.
        Returns: (access_token, refresh_token)
        """
        # Get admin for role
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == admin_id)
        )
        admin = result.scalar_one()

        access_token = self.create_access_token(admin_id, admin.role)
        refresh_token = self.create_refresh_token(admin_id)

        # Store session with hashed refresh token
        refresh_hash = bcrypt.hashpw(
            refresh_token.encode('utf-8'),
            bcrypt.gensalt(rounds=10)
        ).decode('utf-8')

        session = SuperAdminSession(
            admin_id=admin_id,
            refresh_token_hash=refresh_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(session)
        await db.commit()

        return access_token, refresh_token

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> Optional[str]:
        """
        Refresh an access token using a valid refresh token.
        Returns: new access token or None if invalid
        """
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        admin_id = UUID(payload["sub"])

        # Verify session exists
        result = await db.execute(
            select(SuperAdminSession).where(
                SuperAdminSession.admin_id == admin_id,
                SuperAdminSession.expires_at > datetime.utcnow()
            )
        )
        sessions = result.scalars().all()

        # Check if refresh token matches any session
        for session in sessions:
            if bcrypt.checkpw(refresh_token.encode('utf-8'), session.refresh_token_hash.encode('utf-8')):
                # Get admin role
                admin_result = await db.execute(
                    select(SuperAdmin).where(SuperAdmin.id == admin_id, SuperAdmin.is_active == True)
                )
                admin = admin_result.scalar_one_or_none()
                if admin:
                    return self.create_access_token(admin_id, admin.role)

        return None

    async def logout(
        self,
        db: AsyncSession,
        admin_id: UUID,
        refresh_token: str = None
    ):
        """Logout admin by invalidating session"""
        if refresh_token:
            # Find and delete specific session
            result = await db.execute(
                select(SuperAdminSession).where(
                    SuperAdminSession.admin_id == admin_id
                )
            )
            sessions = result.scalars().all()

            for session in sessions:
                if bcrypt.checkpw(refresh_token.encode('utf-8'), session.refresh_token_hash.encode('utf-8')):
                    await db.delete(session)
                    break
        else:
            # Logout from all sessions
            await db.execute(
                SuperAdminSession.__table__.delete().where(
                    SuperAdminSession.admin_id == admin_id
                )
            )

        await db.commit()

    async def setup_mfa(
        self,
        db: AsyncSession,
        admin_id: UUID
    ) -> dict:
        """
        Setup MFA for an admin.
        Returns: {secret, qr_code_url, backup_codes}
        """
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == admin_id)
        )
        admin = result.scalar_one()

        secret = self.generate_mfa_secret()
        backup_codes = self.generate_backup_codes()
        qr_url = self.get_mfa_qr_url(secret, admin.email)

        # Store secret (not enabled until verified)
        admin.mfa_secret = secret
        admin.mfa_backup_codes = backup_codes

        await db.commit()

        return {
            "secret": secret,
            "qr_code_url": qr_url,
            "backup_codes": backup_codes
        }

    async def enable_mfa(
        self,
        db: AsyncSession,
        admin_id: UUID,
        code: str
    ) -> bool:
        """
        Verify and enable MFA for an admin.
        Returns: True if enabled successfully
        """
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == admin_id)
        )
        admin = result.scalar_one()

        if not admin.mfa_secret:
            return False

        if not self.verify_mfa_code(admin.mfa_secret, code):
            return False

        admin.mfa_enabled = True
        await db.commit()

        return True

    async def disable_mfa(
        self,
        db: AsyncSession,
        admin_id: UUID,
        password: str
    ) -> bool:
        """
        Disable MFA for an admin (requires password verification).
        Returns: True if disabled successfully
        """
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == admin_id)
        )
        admin = result.scalar_one()

        if not self.verify_password(password, admin.password_hash):
            return False

        admin.mfa_enabled = False
        admin.mfa_secret = None
        admin.mfa_backup_codes = None

        await db.commit()

        return True

    async def change_password(
        self,
        db: AsyncSession,
        admin_id: UUID,
        current_password: str,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Change admin password.
        Returns: (success, error_message)
        """
        result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == admin_id)
        )
        admin = result.scalar_one()

        if not self.verify_password(current_password, admin.password_hash):
            return False, "Current password is incorrect"

        # Hash new password
        admin.password_hash = self.hash_password(new_password)
        admin.updated_at = datetime.utcnow()

        # Invalidate all sessions (force re-login)
        await db.execute(
            SuperAdminSession.__table__.delete().where(
                SuperAdminSession.admin_id == admin_id
            )
        )

        # Audit log
        audit = SuperAdminAuditLog(
            admin_id=admin_id,
            action="password.change",
            action_category="auth",
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()

        return True, None

    async def check_platform_settings(
        self,
        db: AsyncSession,
        admin: SuperAdmin
    ) -> dict:
        """Check platform security settings for admin"""
        result = await db.execute(select(PlatformSettings).limit(1))
        settings = result.scalar_one_or_none()

        if not settings:
            return {"mfa_required": False, "session_timeout": 60}

        return {
            "mfa_required": settings.enforce_mfa_superadmins,
            "session_timeout": settings.session_timeout_minutes,
            "password_min_length": settings.password_min_length,
            "password_require_special": settings.password_require_special
        }
