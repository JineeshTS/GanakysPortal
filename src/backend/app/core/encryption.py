"""
QA-003: Data Encryption Service
Encryption utilities for sensitive data at rest and in transit
Using AES-256-GCM for authenticated encryption
"""
from typing import Optional, Union
import base64
import hashlib
import hmac
import secrets
import os
from datetime import datetime, timedelta

# Import cryptography library for proper AES-256-GCM
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class EncryptionService:
    """
    Encryption service for sensitive data.

    Features:
    - AES-256-GCM authenticated encryption for data at rest
    - Secure key derivation using PBKDF2
    - Secure hashing
    - Token generation
    - Key management
    """

    # Key derivation parameters
    PBKDF2_ITERATIONS = 100000
    SALT_LENGTH = 32
    KEY_LENGTH = 32  # 256 bits for AES-256
    NONCE_LENGTH = 12  # 96 bits for GCM

    def __init__(self, master_key: Optional[str] = None):
        """Initialize with master key."""
        self.master_key = master_key or os.environ.get(
            'ENCRYPTION_KEY',
            secrets.token_hex(32)
        )
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography library is required for encryption. "
                "Install with: pip install cryptography"
            )

    def encrypt(self, plaintext: str, key: Optional[str] = None) -> str:
        """
        Encrypt plaintext using AES-256-GCM.

        AES-GCM provides both confidentiality and authenticity.
        The authentication tag is automatically appended to the ciphertext.

        Args:
            plaintext: Text to encrypt
            key: Optional encryption key (uses master key if not provided)

        Returns:
            Base64-encoded encrypted data: salt (32) + nonce (12) + ciphertext + tag (16)
        """
        # Generate salt and derive key
        salt = secrets.token_bytes(self.SALT_LENGTH)
        derived_key = self._derive_key(key or self.master_key, salt)

        # Generate nonce (must be unique per encryption with same key)
        nonce = secrets.token_bytes(self.NONCE_LENGTH)

        # Create AES-GCM cipher and encrypt
        aesgcm = AESGCM(derived_key)
        plaintext_bytes = plaintext.encode('utf-8')

        # Encrypt with authentication - tag is automatically appended
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Combine salt + nonce + ciphertext (includes auth tag)
        combined = salt + nonce + ciphertext

        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, ciphertext: str, key: Optional[str] = None) -> str:
        """
        Decrypt ciphertext using AES-256-GCM.

        Verifies authenticity before returning plaintext.
        Raises exception if data has been tampered with.

        Args:
            ciphertext: Base64-encoded encrypted data
            key: Optional decryption key

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails or data is tampered
        """
        try:
            # Decode from base64
            combined = base64.b64decode(ciphertext.encode('utf-8'))

            # Extract components
            salt = combined[:self.SALT_LENGTH]
            nonce = combined[self.SALT_LENGTH:self.SALT_LENGTH + self.NONCE_LENGTH]
            encrypted_data = combined[self.SALT_LENGTH + self.NONCE_LENGTH:]

            # Derive key
            derived_key = self._derive_key(key or self.master_key, salt)

            # Create AES-GCM cipher and decrypt (also verifies auth tag)
            aesgcm = AESGCM(derived_key)
            plaintext_bytes = aesgcm.decrypt(nonce, encrypted_data, None)

            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed - data may be corrupted or tampered: {e}")

    def hash_value(self, value: str, salt: Optional[str] = None) -> str:
        """
        Create secure hash of value.

        Args:
            value: Value to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Hash in format: salt$hash
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            value.encode(),
            salt.encode(),
            self.PBKDF2_ITERATIONS
        )

        return f"{salt}${hash_value.hex()}"

    def verify_hash(self, value: str, hashed: str) -> bool:
        """Verify value against hash."""
        try:
            salt, expected_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                value.encode(),
                salt.encode(),
                self.PBKDF2_ITERATIONS
            )
            return hmac.compare_digest(new_hash.hex(), expected_hash)
        except Exception:
            return False

    def generate_token(self, length: int = 32) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(length)

    def generate_api_key(self) -> str:
        """Generate API key with prefix."""
        prefix = "gp"  # GanaPortal prefix
        key = secrets.token_hex(24)
        return f"{prefix}_{key}"

    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_otp(self, length: int = 6) -> str:
        """Generate numeric OTP."""
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.

        Uses PBKDF2 with SHA-256 and 100,000 iterations for key derivation.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode())


class TokenManager:
    """
    Manage authentication and session tokens.

    Features:
    - JWT token generation
    - Refresh token management
    - Token blacklisting
    - Session management
    """

    # Token configuration - Secure defaults
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Reduced from 30 for security
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "HS256"

    def __init__(self, secret_key: str):
        """Initialize with secret key."""
        self.secret_key = secret_key
        self._blacklist: set = set()

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str,
        company_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token."""
        import jwt

        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "company_id": company_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token."""
        import jwt

        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_hex(16),  # Token ID
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode token."""
        import jwt

        try:
            # Check blacklist
            if token in self._blacklist:
                return None

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM]
            )

            if payload.get("type") != token_type:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist."""
        self._blacklist.add(token)

    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self._blacklist

    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token."""
        import jwt

        expire = datetime.utcnow() + timedelta(hours=1)

        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "password_reset",
            "jti": secrets.token_hex(16),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

    def create_email_verification_token(self, user_id: str, email: str) -> str:
        """Create email verification token."""
        import jwt

        expire = datetime.utcnow() + timedelta(days=7)

        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "email_verification",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)


class FieldLevelEncryption:
    """
    Field-level encryption for sensitive database columns.

    Encrypts specific fields: PAN, Aadhaar, bank account numbers, etc.
    """

    SENSITIVE_FIELDS = [
        'pan', 'aadhaar', 'account_number', 'ifsc_code',
        'salary', 'ctc', 'bank_details', 'tax_details',
    ]

    def __init__(self, encryption_service: EncryptionService):
        """Initialize with encryption service."""
        self.encryption = encryption_service

    def encrypt_model_fields(self, data: dict, fields: list = None) -> dict:
        """Encrypt sensitive fields in model data."""
        fields_to_encrypt = fields or self.SENSITIVE_FIELDS
        encrypted = data.copy()

        for field in fields_to_encrypt:
            if field in encrypted and encrypted[field]:
                value = encrypted[field]
                if isinstance(value, dict):
                    value = str(value)
                encrypted[field] = self.encryption.encrypt(str(value))

        return encrypted

    def decrypt_model_fields(self, data: dict, fields: list = None) -> dict:
        """Decrypt sensitive fields in model data."""
        fields_to_decrypt = fields or self.SENSITIVE_FIELDS
        decrypted = data.copy()

        for field in fields_to_decrypt:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = self.encryption.decrypt(decrypted[field])
                except Exception:
                    # Field might not be encrypted
                    pass

        return decrypted


# Singleton instances
encryption_service = EncryptionService()
token_manager = TokenManager(
    secret_key=os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
)
field_encryption = FieldLevelEncryption(encryption_service)
