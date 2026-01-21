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
from datetime import datetime, timedelta, timezone
from jose import jwt  # python-jose for JWT operations

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
    - Key versioning and rotation support
    """

    # Key derivation parameters
    PBKDF2_ITERATIONS = 100000
    SALT_LENGTH = 32
    KEY_LENGTH = 32  # 256 bits for AES-256
    NONCE_LENGTH = 12  # 96 bits for GCM
    VERSION_LENGTH = 1  # Key version byte

    # Current key version (increment when rotating keys)
    CURRENT_KEY_VERSION = 1

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize with master key and optional old keys for rotation support.

        Environment variables:
        - ENCRYPTION_KEY: Current encryption key (required)
        - ENCRYPTION_KEY_VERSION: Current key version (optional, default=1)
        - ENCRYPTION_KEY_V0: Previous key version 0 for decryption (optional)
        - ENCRYPTION_KEY_V1, V2, etc.: Additional key versions (optional)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography library is required for encryption. "
                "Install with: pip install cryptography"
            )

        # SECURITY: Encryption key must be provided or set via environment
        # Never fall back to a random key - data would be unrecoverable
        if master_key:
            self.master_key = master_key
        else:
            env_key = os.environ.get('ENCRYPTION_KEY')
            if not env_key:
                raise ValueError(
                    "ENCRYPTION_KEY must be set in environment. "
                    "Generate with: openssl rand -base64 32"
                )
            if len(env_key) < 32:
                raise ValueError(
                    "ENCRYPTION_KEY must be at least 32 characters. "
                    "Generate with: openssl rand -base64 32"
                )
            self.master_key = env_key

        # Get current key version from environment
        self.current_version = int(os.environ.get('ENCRYPTION_KEY_VERSION', str(self.CURRENT_KEY_VERSION)))

        # Build key registry for rotation support
        # Keys indexed by version for decryption of old data
        self._key_registry: dict[int, str] = {}
        self._key_registry[self.current_version] = self.master_key

        # Load old key versions for decryption during rotation
        # Version 0 = legacy data encrypted without version prefix
        legacy_key = os.environ.get('ENCRYPTION_KEY_V0')
        if legacy_key:
            self._key_registry[0] = legacy_key

        # Load versioned keys (V1, V2, etc.)
        for version in range(1, 100):  # Support up to 100 key versions
            key = os.environ.get(f'ENCRYPTION_KEY_V{version}')
            if key:
                self._key_registry[version] = key

    def get_key_for_version(self, version: int) -> Optional[str]:
        """Get encryption key for a specific version."""
        return self._key_registry.get(version)

    def list_key_versions(self) -> list[int]:
        """List all available key versions."""
        return sorted(self._key_registry.keys())

    def encrypt(self, plaintext: str, key: Optional[str] = None) -> str:
        """
        Encrypt plaintext using AES-256-GCM with key versioning.

        AES-GCM provides both confidentiality and authenticity.
        The authentication tag is automatically appended to the ciphertext.

        Args:
            plaintext: Text to encrypt
            key: Optional encryption key (uses master key if not provided)

        Returns:
            Base64-encoded encrypted data: version (1) + salt (32) + nonce (12) + ciphertext + tag (16)
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

        # Combine version + salt + nonce + ciphertext (includes auth tag)
        # Version byte allows future key rotation
        version_byte = bytes([self.current_version])
        combined = version_byte + salt + nonce + ciphertext

        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, ciphertext: str, key: Optional[str] = None) -> str:
        """
        Decrypt ciphertext using AES-256-GCM with key version support.

        Verifies authenticity before returning plaintext.
        Supports both versioned (new) and legacy (old) encrypted data.
        Raises exception if data has been tampered with.

        Args:
            ciphertext: Base64-encoded encrypted data
            key: Optional decryption key (overrides key registry lookup)

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails or data is tampered
        """
        try:
            # Decode from base64
            combined = base64.b64decode(ciphertext.encode('utf-8'))

            # Determine if this is versioned or legacy data
            # Legacy format: salt (32) + nonce (12) + ciphertext + tag (16) = min 60 bytes
            # Versioned format: version (1) + salt (32) + nonce (12) + ciphertext + tag (16) = min 61 bytes
            # We detect version by checking if first byte is a valid version number
            # and the data is at least 61 bytes (version + minimum encrypted data)
            version = 0  # Default to legacy
            offset = 0

            if len(combined) >= self.VERSION_LENGTH + self.SALT_LENGTH + self.NONCE_LENGTH + 16:
                potential_version = combined[0]
                # Version 0 is reserved for legacy, versions 1-99 are valid
                if 1 <= potential_version <= 99:
                    version = potential_version
                    offset = self.VERSION_LENGTH

            # Extract components based on format
            salt = combined[offset:offset + self.SALT_LENGTH]
            nonce = combined[offset + self.SALT_LENGTH:offset + self.SALT_LENGTH + self.NONCE_LENGTH]
            encrypted_data = combined[offset + self.SALT_LENGTH + self.NONCE_LENGTH:]

            # Get the appropriate key
            if key:
                decryption_key = key
            else:
                decryption_key = self._key_registry.get(version)
                if not decryption_key:
                    # Fallback to current key for legacy data
                    decryption_key = self.master_key

            # Derive key
            derived_key = self._derive_key(decryption_key, salt)

            # Create AES-GCM cipher and decrypt (also verifies auth tag)
            aesgcm = AESGCM(derived_key)
            plaintext_bytes = aesgcm.decrypt(nonce, encrypted_data, None)

            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed - data may be corrupted or tampered: {e}")

    def get_data_key_version(self, ciphertext: str) -> int:
        """
        Get the key version used to encrypt data.

        Args:
            ciphertext: Base64-encoded encrypted data

        Returns:
            Key version (0 for legacy data, 1+ for versioned data)
        """
        try:
            combined = base64.b64decode(ciphertext.encode('utf-8'))
            if len(combined) >= self.VERSION_LENGTH + self.SALT_LENGTH + self.NONCE_LENGTH + 16:
                potential_version = combined[0]
                if 1 <= potential_version <= 99:
                    return potential_version
            return 0  # Legacy data
        except Exception:
            return -1  # Invalid data

    def needs_re_encryption(self, ciphertext: str) -> bool:
        """
        Check if data needs to be re-encrypted with current key.

        Args:
            ciphertext: Base64-encoded encrypted data

        Returns:
            True if data should be re-encrypted with current key
        """
        data_version = self.get_data_key_version(ciphertext)
        return data_version != self.current_version

    def re_encrypt(self, ciphertext: str) -> str:
        """
        Re-encrypt data with the current key version.

        Used for key rotation - decrypt with old key, encrypt with new.

        Args:
            ciphertext: Base64-encoded encrypted data

        Returns:
            Re-encrypted data with current key version
        """
        # Decrypt with appropriate old key
        plaintext = self.decrypt(ciphertext)
        # Re-encrypt with current key
        return self.encrypt(plaintext)

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
    - Token blacklisting (Redis-backed for persistence)
    - Session management
    """

    # Token configuration - Secure defaults
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Reduced from 30 for security
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ALGORITHM = "HS256"
    BLACKLIST_PREFIX = "token_blacklist:"

    def __init__(self, secret_key: str):
        """Initialize with secret key."""
        if not secret_key:
            raise ValueError(
                "JWT secret key must be provided. "
                "Set JWT_SECRET_KEY in environment."
            )
        if len(secret_key) < 32:
            raise ValueError(
                "JWT secret key must be at least 32 characters for security."
            )
        self.secret_key = secret_key
        self._redis_client = None
        # Fallback in-memory blacklist only used if Redis unavailable
        self._memory_blacklist: set = set()

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str,
        company_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT access token."""

        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "company_id": company_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token."""

        expire = datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_hex(16),  # Token ID
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode token."""

        try:
            # Check blacklist (Redis-backed with in-memory fallback)
            if self.is_blacklisted(token):
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

    def _get_redis(self):
        """Get Redis client for blacklist storage."""
        if self._redis_client is None:
            try:
                import redis
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self._redis_client.ping()
            except Exception:
                self._redis_client = None
        return self._redis_client

    def blacklist_token(self, token: str, expires_in: int = None) -> None:
        """
        Add token to blacklist.

        Uses Redis for persistence across restarts.
        Falls back to in-memory if Redis unavailable.
        """
        # Default expiry: 7 days (max token lifetime)
        if expires_in is None:
            expires_in = self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        redis_client = self._get_redis()
        if redis_client:
            try:
                key = f"{self.BLACKLIST_PREFIX}{hashlib.sha256(token.encode()).hexdigest()}"
                redis_client.setex(key, expires_in, "1")
                return
            except Exception:
                pass

        # Fallback to in-memory
        self._memory_blacklist.add(token)

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Checks Redis first, then in-memory fallback.
        """
        redis_client = self._get_redis()
        if redis_client:
            try:
                key = f"{self.BLACKLIST_PREFIX}{hashlib.sha256(token.encode()).hexdigest()}"
                return redis_client.exists(key) > 0
            except Exception:
                pass

        # Fallback to in-memory
        return token in self._memory_blacklist

    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token."""

        expire = datetime.now(timezone.utc) + timedelta(hours=1)

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

        expire = datetime.now(timezone.utc) + timedelta(days=7)

        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "type": "email_verification",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)


class EncryptedString:
    """
    SQLAlchemy TypeDecorator for automatic field encryption.

    Usage in models:
        from app.core.encryption import EncryptedString
        aadhaar = Column(EncryptedString(), nullable=True)
    """

    def __init__(self):
        from sqlalchemy import TypeDecorator, String
        self._base = TypeDecorator
        self._impl = String(500)  # Encrypted values are longer

    @staticmethod
    def create_type():
        """Create the actual TypeDecorator class."""
        from sqlalchemy import TypeDecorator, String

        class _EncryptedString(TypeDecorator):
            impl = String(500)
            cache_ok = True

            def process_bind_param(self, value, dialect):
                """Encrypt value before saving to database."""
                if value is not None:
                    try:
                        svc = get_encryption_service()
                        if svc:
                            return svc.encrypt(str(value))
                    except Exception:
                        pass  # Return unencrypted if encryption service unavailable
                return value

            def process_result_value(self, value, dialect):
                """Decrypt value when reading from database."""
                if value is not None:
                    try:
                        svc = get_encryption_service()
                        if svc:
                            return svc.decrypt(value)
                    except Exception:
                        pass  # Return as-is if decryption fails
                return value

        return _EncryptedString


# Create the type for export
try:
    EncryptedStringType = EncryptedString.create_type()
except Exception:
    EncryptedStringType = None


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


class KeyRotationManager:
    """
    Manages encryption key rotation for gradual data migration.

    Usage:
        1. Generate new key: openssl rand -base64 32
        2. Set new key as ENCRYPTION_KEY, increment ENCRYPTION_KEY_VERSION
        3. Set old key as ENCRYPTION_KEY_V{old_version}
        4. Run rotate_table() for each table with encrypted data
        5. After all data migrated, remove old key from environment

    Example environment for rotation from v1 to v2:
        ENCRYPTION_KEY=new_key_here
        ENCRYPTION_KEY_VERSION=2
        ENCRYPTION_KEY_V1=old_key_here
    """

    def __init__(self, encryption_service: EncryptionService):
        """Initialize with encryption service."""
        self.encryption = encryption_service

    def get_rotation_status(self) -> dict:
        """
        Get current key rotation status.

        Returns:
            Dictionary with current version, available versions, and status
        """
        return {
            "current_version": self.encryption.current_version,
            "available_versions": self.encryption.list_key_versions(),
            "has_legacy_key": 0 in self.encryption._key_registry,
            "ready_for_rotation": len(self.encryption._key_registry) > 1
        }

    async def rotate_encrypted_field(
        self,
        db_session,
        model_class,
        field_name: str,
        batch_size: int = 100
    ) -> dict:
        """
        Rotate encryption for a specific field in a model.

        Args:
            db_session: SQLAlchemy async session
            model_class: SQLAlchemy model class
            field_name: Name of the encrypted field
            batch_size: Number of records to process per batch

        Returns:
            Dictionary with rotation statistics
        """
        from sqlalchemy import select, update

        stats = {
            "total": 0,
            "rotated": 0,
            "skipped": 0,
            "errors": 0
        }

        # Get all records with encrypted field
        offset = 0
        while True:
            stmt = select(model_class).offset(offset).limit(batch_size)
            result = await db_session.execute(stmt)
            records = result.scalars().all()

            if not records:
                break

            for record in records:
                stats["total"] += 1
                encrypted_value = getattr(record, field_name, None)

                if not encrypted_value:
                    stats["skipped"] += 1
                    continue

                try:
                    if self.encryption.needs_re_encryption(encrypted_value):
                        # Re-encrypt with current key
                        new_value = self.encryption.re_encrypt(encrypted_value)
                        setattr(record, field_name, new_value)
                        stats["rotated"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    stats["errors"] += 1

            await db_session.commit()
            offset += batch_size

        return stats

    def check_field_needs_rotation(self, encrypted_value: str) -> bool:
        """Check if a single encrypted value needs rotation."""
        if not encrypted_value:
            return False
        return self.encryption.needs_re_encryption(encrypted_value)


# Singleton instances
# These require environment variables to be set - no insecure defaults
def _get_encryption_service():
    """Get or create encryption service singleton."""
    return EncryptionService()


def _get_token_manager():
    """Get or create token manager singleton."""
    secret_key = os.environ.get('JWT_SECRET_KEY')
    if not secret_key:
        raise ValueError(
            "JWT_SECRET_KEY environment variable must be set. "
            "Generate with: openssl rand -base64 64"
        )
    return TokenManager(secret_key=secret_key)


# Lazy initialization to allow app startup configuration
_encryption_service = None
_token_manager = None


def get_encryption_service() -> EncryptionService:
    """Get encryption service singleton (lazy initialization)."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = _get_encryption_service()
    return _encryption_service


def get_token_manager() -> TokenManager:
    """Get token manager singleton (lazy initialization)."""
    global _token_manager
    if _token_manager is None:
        _token_manager = _get_token_manager()
    return _token_manager


_key_rotation_manager = None


def get_key_rotation_manager() -> KeyRotationManager:
    """Get key rotation manager singleton (lazy initialization)."""
    global _key_rotation_manager
    if _key_rotation_manager is None:
        _key_rotation_manager = KeyRotationManager(get_encryption_service())
    return _key_rotation_manager


# Backward compatibility - these will raise errors if env vars not set
# Applications should use get_encryption_service() and get_token_manager() instead
encryption_service = property(lambda self: get_encryption_service())
token_manager = property(lambda self: get_token_manager())

# Direct access for imports that expect these to exist immediately
# Will fail fast if environment is not configured
try:
    encryption_service = get_encryption_service()
    token_manager = get_token_manager()
    field_encryption = FieldLevelEncryption(encryption_service)
    key_rotation_manager = KeyRotationManager(encryption_service)
except ValueError as e:
    import warnings
    warnings.warn(f"Encryption services not initialized: {e}. Set required environment variables.")
    encryption_service = None
    token_manager = None
    field_encryption = None
    key_rotation_manager = None
