"""
Custom SQLAlchemy types for GanaPortal.
WBS Reference: Task 2.1.1.1 (FIX-WBS)
"""
from typing import Optional

from sqlalchemy import String, TypeDecorator

from app.core.security import encrypt_sensitive_data, decrypt_sensitive_data


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy TypeDecorator for transparent encryption/decryption.

    Automatically encrypts data when writing to the database and
    decrypts when reading. Uses Fernet symmetric encryption.

    Usage:
        pan_number: Mapped[Optional[str]] = mapped_column(EncryptedString(500))

    Note:
        - Encrypted values are longer than originals, so use appropriate column size
        - Empty/None values are stored as-is (not encrypted)
        - Searching encrypted fields requires exact match after encryption
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 500, *args, **kwargs):
        """
        Initialize EncryptedString with column length.

        Args:
            length: Maximum length of encrypted value (default 500)
        """
        super().__init__(*args, **kwargs)
        self.impl = String(length)

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Encrypt value before storing in database.

        Called when data is being written to the database.
        """
        if value is None or value == "":
            return value
        return encrypt_sensitive_data(value)

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Decrypt value when reading from database.

        Called when data is being read from the database.
        """
        if value is None or value == "":
            return value
        try:
            return decrypt_sensitive_data(value)
        except Exception:
            # If decryption fails (e.g., data was stored unencrypted),
            # return the original value. This helps with migration.
            return value
