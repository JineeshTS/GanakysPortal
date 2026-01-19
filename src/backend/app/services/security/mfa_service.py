"""
MFA Service
Manages multi-factor authentication
"""
import secrets
import pyotp
import base64
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.security import MFAConfig, MFAMethod
from app.schemas.security import MFAConfigResponse, EnableTOTPResponse
from app.core.datetime_utils import utc_now
from app.core.constants import MFA_BACKUP_CODES_COUNT, TOKEN_BYTES


class MFAService:
    """Service for managing MFA"""

    async def get_mfa_config(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> MFAConfigResponse:
        """Get MFA configuration for user"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            config = MFAConfig(user_id=user_id)
            db.add(config)
            await db.commit()
            await db.refresh(config)

        return MFAConfigResponse.model_validate(config)

    async def _get_or_create_config(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> MFAConfig:
        """Get or create MFA config"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            config = MFAConfig(user_id=user_id)
            db.add(config)
            await db.flush()

        return config

    async def enable_totp(
        self,
        db: AsyncSession,
        user_id: UUID,
        email: str
    ) -> EnableTOTPResponse:
        """Enable TOTP and return setup data"""
        config = await self._get_or_create_config(db, user_id)

        # Generate secret
        secret = pyotp.random_base32()
        config.totp_secret = secret

        # Generate backup codes
        backup_codes = [secrets.token_hex(TOKEN_BYTES).upper() for _ in range(MFA_BACKUP_CODES_COUNT)]
        config.backup_codes = backup_codes
        config.backup_codes_generated = True
        config.backup_codes_generated_at = utc_now()

        await db.commit()

        # Generate QR code URL
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name="Ganakys Codilla"
        )

        return EnableTOTPResponse(
            secret=secret,
            qr_code_url=provisioning_uri,
            backup_codes=backup_codes
        )

    async def verify_totp(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> bool:
        """Verify TOTP code and enable if valid"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.totp_secret:
            return False

        totp = pyotp.TOTP(config.totp_secret)
        if totp.verify(code):
            config.totp_enabled = True
            config.totp_verified_at = utc_now()
            config.preferred_method = MFAMethod.totp
            await db.commit()
            return True

        return False

    async def disable_totp(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> bool:
        """Disable TOTP after verification"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.totp_secret:
            return False

        totp = pyotp.TOTP(config.totp_secret)
        if totp.verify(code):
            config.totp_enabled = False
            config.totp_secret = None
            config.totp_verified_at = None

            # Update preferred method if TOTP was preferred
            if config.preferred_method == MFAMethod.totp:
                if config.email_enabled:
                    config.preferred_method = MFAMethod.email
                elif config.sms_enabled:
                    config.preferred_method = MFAMethod.sms
                else:
                    config.preferred_method = None

            await db.commit()
            return True

        return False

    async def verify_totp_code(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> bool:
        """Verify TOTP code for authentication"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.totp_enabled or not config.totp_secret:
            return False

        totp = pyotp.TOTP(config.totp_secret)
        return totp.verify(code)

    async def enable_sms(
        self,
        db: AsyncSession,
        user_id: UUID,
        phone_number: str
    ) -> None:
        """Enable SMS MFA (sends verification code)"""
        config = await self._get_or_create_config(db, user_id)
        config.sms_phone_number = phone_number
        await db.commit()

        # TODO: Send verification SMS
        # sms_service.send_verification(phone_number, code)

    async def verify_sms(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> bool:
        """Verify SMS code and enable if valid"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            return False

        # TODO: Verify the code against stored verification code
        # For now, assume verification passes
        config.sms_enabled = True
        config.sms_verified_at = utc_now()
        if not config.preferred_method:
            config.preferred_method = MFAMethod.sms
        await db.commit()
        return True

    async def enable_email(
        self,
        db: AsyncSession,
        user_id: UUID,
        email: str
    ) -> None:
        """Enable email MFA (sends verification code)"""
        config = await self._get_or_create_config(db, user_id)
        config.email_address = email
        await db.commit()

        # TODO: Send verification email
        # email_service.send_verification(email, code)

    async def generate_backup_codes(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[str]:
        """Generate new backup codes"""
        config = await self._get_or_create_config(db, user_id)

        backup_codes = [secrets.token_hex(TOKEN_BYTES).upper() for _ in range(MFA_BACKUP_CODES_COUNT)]
        config.backup_codes = backup_codes
        config.backup_codes_generated = True
        config.backup_codes_used = 0
        config.backup_codes_generated_at = utc_now()

        await db.commit()
        return backup_codes

    async def verify_backup_code(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> bool:
        """Verify and consume a backup code"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.backup_codes:
            return False

        # Check if code exists
        code_upper = code.upper().replace("-", "")
        if code_upper in config.backup_codes:
            # Remove used code
            config.backup_codes = [c for c in config.backup_codes if c != code_upper]
            config.backup_codes_used += 1
            await db.commit()
            return True

        return False

    async def is_mfa_enabled(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> bool:
        """Check if user has any MFA enabled"""
        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            return False

        return (
            config.totp_enabled or
            config.sms_enabled or
            config.email_enabled or
            config.hardware_key_enabled
        )
