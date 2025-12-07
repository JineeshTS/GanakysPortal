"""
Security utilities for authentication and encryption.
"""
import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash for the given password."""
    return pwd_context.hash(password)


def generate_temp_password(length: int = 12) -> str:
    """Generate a secure temporary password."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(32),  # Unique token ID for blacklisting
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_password_reset_token(email: str) -> str:
    """Generate a password reset token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return the email."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


# Encryption for sensitive data (PAN, Aadhaar, Bank Account)
def _get_fernet() -> Fernet:
    """Get Fernet instance for encryption/decryption."""
    # Derive a valid Fernet key from the settings key
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like PAN, Aadhaar, Bank Account."""
    if not data:
        return data
    fernet = _get_fernet()
    return fernet.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    if not encrypted_data:
        return encrypted_data
    fernet = _get_fernet()
    return fernet.decrypt(encrypted_data.encode()).decode()


def mask_pan(pan: str) -> str:
    """Mask PAN number for display (e.g., ABCDE****F)."""
    if not pan or len(pan) < 10:
        return pan
    return f"{pan[:5]}****{pan[-1]}"


def mask_aadhaar(aadhaar: str) -> str:
    """Mask Aadhaar number for display (e.g., XXXX-XXXX-1234)."""
    if not aadhaar or len(aadhaar) < 12:
        return aadhaar
    return f"XXXX-XXXX-{aadhaar[-4:]}"


def mask_bank_account(account_number: str) -> str:
    """Mask bank account for display (e.g., XXXXXX1234)."""
    if not account_number or len(account_number) < 4:
        return account_number
    return f"{'X' * (len(account_number) - 4)}{account_number[-4:]}"
