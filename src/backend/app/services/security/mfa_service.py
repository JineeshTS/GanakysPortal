"""
MFA Service
Manages multi-factor authentication
"""
import secrets
import pyotp
import base64
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.security import MFAConfig, MFAMethod
from app.schemas.security import MFAConfigResponse, EnableTOTPResponse
from app.core.datetime_utils import utc_now
from app.core.constants import MFA_BACKUP_CODES_COUNT, TOKEN_BYTES

logger = logging.getLogger(__name__)

# Rate limiting configuration
MAX_MFA_ATTEMPTS = 5
MFA_LOCKOUT_DURATION_MINUTES = 15
VERIFICATION_CODE_EXPIRY_MINUTES = 10
VERIFICATION_CODE_LENGTH = 6

# In-memory rate limiting store (in production, use Redis)
_rate_limit_store: Dict[str, Tuple[int, datetime]] = {}


def _hash_code(code: str) -> str:
    """Hash a verification/backup code for secure storage."""
    return hashlib.sha256(code.encode()).hexdigest()


def _generate_verification_code() -> str:
    """Generate a random numeric verification code."""
    return ''.join(secrets.choice('0123456789') for _ in range(VERIFICATION_CODE_LENGTH))


class MFAService:
    """Service for managing MFA"""

    def _check_rate_limit(self, user_id: UUID, action: str = "verify") -> Tuple[bool, Optional[int]]:
        """
        Check if user is rate limited for MFA attempts.
        Returns (is_allowed, seconds_until_unlock)
        """
        key = f"{user_id}:{action}"
        now = datetime.utcnow()

        if key in _rate_limit_store:
            attempts, first_attempt_time = _rate_limit_store[key]
            lockout_end = first_attempt_time + timedelta(minutes=MFA_LOCKOUT_DURATION_MINUTES)

            if attempts >= MAX_MFA_ATTEMPTS:
                if now < lockout_end:
                    seconds_remaining = int((lockout_end - now).total_seconds())
                    return False, seconds_remaining
                else:
                    # Lockout expired, reset counter
                    del _rate_limit_store[key]
                    return True, None

        return True, None

    def _record_attempt(self, user_id: UUID, action: str = "verify", success: bool = False):
        """Record an MFA verification attempt for rate limiting."""
        key = f"{user_id}:{action}"
        now = datetime.utcnow()

        if success:
            # Reset on successful attempt
            if key in _rate_limit_store:
                del _rate_limit_store[key]
            return

        if key in _rate_limit_store:
            attempts, first_time = _rate_limit_store[key]
            _rate_limit_store[key] = (attempts + 1, first_time)
        else:
            _rate_limit_store[key] = (1, now)

        logger.warning(f"MFA attempt failed for user {user_id}, action {action}")

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

        # Generate backup codes (plain for user, hashed for storage)
        plain_backup_codes = [secrets.token_hex(TOKEN_BYTES).upper() for _ in range(MFA_BACKUP_CODES_COUNT)]
        config.backup_codes = [_hash_code(code) for code in plain_backup_codes]
        config.backup_codes_generated = True
        config.backup_codes_used = 0
        config.backup_codes_generated_at = utc_now()

        await db.commit()
        logger.info(f"TOTP enabled for user {user_id}")

        # Generate QR code URL
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name="Ganakys Codilla"
        )

        return EnableTOTPResponse(
            secret=secret,
            qr_code_url=provisioning_uri,
            backup_codes=plain_backup_codes
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
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify TOTP code for authentication.
        Returns (success, error_message)
        """
        # Check rate limit first
        is_allowed, seconds_remaining = self._check_rate_limit(user_id, "totp")
        if not is_allowed:
            logger.warning(f"TOTP verification rate limited for user {user_id}")
            return False, f"Too many attempts. Try again in {seconds_remaining} seconds."

        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.totp_enabled or not config.totp_secret:
            return False, "TOTP not configured"

        totp = pyotp.TOTP(config.totp_secret)
        if totp.verify(code):
            self._record_attempt(user_id, "totp", success=True)
            return True, None

        self._record_attempt(user_id, "totp", success=False)
        return False, "Invalid TOTP code"

    async def enable_sms(
        self,
        db: AsyncSession,
        user_id: UUID,
        phone_number: str
    ) -> str:
        """
        Enable SMS MFA (sends verification code).
        Returns the verification code (in production, this would be sent via SMS).
        """
        config = await self._get_or_create_config(db, user_id)
        config.sms_phone_number = phone_number

        # Generate verification code
        verification_code = _generate_verification_code()
        config.sms_verification_code = _hash_code(verification_code)
        config.sms_verification_code_expires = utc_now() + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES)

        await db.commit()

        # In production, send SMS via service
        # sms_service.send_verification(phone_number, verification_code)
        logger.info(f"SMS verification code generated for user {user_id}")

        return verification_code

    async def verify_sms(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify SMS code and enable if valid.
        Returns (success, error_message)
        """
        # Check rate limit first
        is_allowed, seconds_remaining = self._check_rate_limit(user_id, "sms")
        if not is_allowed:
            logger.warning(f"SMS verification rate limited for user {user_id}")
            return False, f"Too many attempts. Try again in {seconds_remaining} seconds."

        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            return False, "MFA not configured"

        # Check if verification code exists and is not expired
        if not config.sms_verification_code:
            return False, "No verification code pending"

        if config.sms_verification_code_expires and utc_now() > config.sms_verification_code_expires:
            # Clear expired code
            config.sms_verification_code = None
            config.sms_verification_code_expires = None
            await db.commit()
            return False, "Verification code expired. Please request a new code."

        # Verify the code against stored hash
        if _hash_code(code) == config.sms_verification_code:
            config.sms_enabled = True
            config.sms_verified_at = utc_now()
            config.sms_verification_code = None  # Clear after successful verification
            config.sms_verification_code_expires = None
            if not config.preferred_method:
                config.preferred_method = MFAMethod.sms
            await db.commit()
            self._record_attempt(user_id, "sms", success=True)
            return True, None

        self._record_attempt(user_id, "sms", success=False)
        return False, "Invalid verification code"

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
        """
        Generate new backup codes.
        Returns plain codes to display to user (store hashed versions in DB).
        """
        config = await self._get_or_create_config(db, user_id)

        # Generate plain codes for user display
        plain_codes = [secrets.token_hex(TOKEN_BYTES).upper() for _ in range(MFA_BACKUP_CODES_COUNT)]

        # Store hashed versions for security
        config.backup_codes = [_hash_code(code) for code in plain_codes]
        config.backup_codes_generated = True
        config.backup_codes_used = 0
        config.backup_codes_generated_at = utc_now()

        await db.commit()
        logger.info(f"Generated {len(plain_codes)} new backup codes for user {user_id}")
        return plain_codes

    async def verify_backup_code(
        self,
        db: AsyncSession,
        user_id: UUID,
        code: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify and consume a backup code.
        Returns (success, error_message)
        """
        # Check rate limit first
        is_allowed, seconds_remaining = self._check_rate_limit(user_id, "backup")
        if not is_allowed:
            logger.warning(f"Backup code verification rate limited for user {user_id}")
            return False, f"Too many attempts. Try again in {seconds_remaining} seconds."

        result = await db.execute(
            select(MFAConfig).where(MFAConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()

        if not config or not config.backup_codes:
            return False, "No backup codes configured"

        # Normalize input code
        code_upper = code.upper().replace("-", "")
        code_hash = _hash_code(code_upper)

        # Check if hashed code exists in backup codes
        # Support both hashed (new) and plain (legacy) formats
        if code_hash in config.backup_codes:
            # Remove used code (hashed format)
            config.backup_codes = [c for c in config.backup_codes if c != code_hash]
            config.backup_codes_used += 1
            await db.commit()
            self._record_attempt(user_id, "backup", success=True)
            logger.info(f"Backup code used for user {user_id}. Remaining: {len(config.backup_codes)}")
            return True, None
        elif code_upper in config.backup_codes:
            # Legacy plain format - remove and migrate
            config.backup_codes = [c for c in config.backup_codes if c != code_upper]
            config.backup_codes_used += 1
            await db.commit()
            self._record_attempt(user_id, "backup", success=True)
            logger.info(f"Backup code (legacy) used for user {user_id}. Remaining: {len(config.backup_codes)}")
            return True, None

        self._record_attempt(user_id, "backup", success=False)
        return False, "Invalid backup code"

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
