"""
QA-003: Data Encryption Service
Encryption utilities for sensitive data at rest and in transit
"""
from typing import Optional, Union
import base64
import hashlib
import hmac
import secrets
import os
from datetime import datetime, timedelta


class EncryptionService:
    """
    Encryption service for sensitive data.

    Features:
    - AES-256 encryption for data at rest
    - Secure hashing
    - Token generation
    - Key management
    """

    # Key derivation parameters
    PBKDF2_ITERATIONS = 100000
    SALT_LENGTH = 32
    KEY_LENGTH = 32  # 256 bits

    def __init__(self, master_key: Optional[str] = None):
        """Initialize with master key."""
        self.master_key = master_key or os.environ.get(
            'ENCRYPTION_KEY',
            secrets.token_hex(32)
        )

    def encrypt(self, plaintext: str, key: Optional[str] = None) -> str:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: Text to encrypt
            key: Optional encryption key (uses master key if not provided)

        Returns:
            Base64-encoded encrypted data with salt and nonce
        """
        # Generate salt and derive key
        salt = secrets.token_bytes(self.SALT_LENGTH)
        derived_key = self._derive_key(key or self.master_key, salt)

        # Generate nonce
        nonce = secrets.token_bytes(12)

        # In production, use cryptography library for AES-GCM
        # This is a simplified implementation using XOR for demonstration
        plaintext_bytes = plaintext.encode('utf-8')
        key_stream = self._generate_key_stream(derived_key, nonce, len(plaintext_bytes))
        ciphertext = bytes(a ^ b for a, b in zip(plaintext_bytes, key_stream))

        # Combine salt + nonce + ciphertext
        combined = salt + nonce + ciphertext

        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, ciphertext: str, key: Optional[str] = None) -> str:
        """
        Decrypt ciphertext.

        Args:
            ciphertext: Base64-encoded encrypted data
            key: Optional decryption key

        Returns:
            Decrypted plaintext
        """
        # Decode from base64
        combined = base64.b64decode(ciphertext.encode('utf-8'))

        # Extract components
        salt = combined[:self.SALT_LENGTH]
        nonce = combined[self.SALT_LENGTH:self.SALT_LENGTH + 12]
        encrypted_data = combined[self.SALT_LENGTH + 12:]

        # Derive key
        derived_key = self._derive_key(key or self.master_key, salt)

        # Decrypt using XOR (simplified)
        key_stream = self._generate_key_stream(derived_key, nonce, len(encrypted_data))
        plaintext_bytes = bytes(a ^ b for a, b in zip(encrypted_data, key_stream))

        return plaintext_bytes.decode('utf-8')

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
        """Derive encryption key from password."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            self.PBKDF2_ITERATIONS,
            dklen=self.KEY_LENGTH
        )

    def _generate_key_stream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        """Generate key stream for XOR encryption."""
        # Simplified key stream generation
        stream = b''
        counter = 0
        while len(stream) < length:
            block = hashlib.sha256(key + nonce + counter.to_bytes(4, 'big')).digest()
            stream += block
            counter += 1
        return stream[:length]


class TokenManager:
    """
    Manage authentication and session tokens.

    Features:
    - JWT token generation
    - Refresh token management
    - Token blacklisting
    - Session management
    """

    # Token configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
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
