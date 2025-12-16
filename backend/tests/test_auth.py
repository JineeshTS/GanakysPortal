"""
Authentication tests for GanaPortal.
WBS Reference: Task 30.1.1.1.3
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_password_reset_token,
    verify_password_reset_token,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    mask_pan,
    mask_aadhaar,
    mask_bank_account,
)
from app.models.user import User, UserRole


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_password_hash_is_different_from_plain(self):
        """Password hash should be different from plain password."""
        password = "MySecurePassword123!"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_password_verification_success(self):
        """Correct password should verify successfully."""
        password = "MySecurePassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Incorrect password should fail verification."""
        password = "MySecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Same password should produce different hashes (due to salt)."""
        password = "MySecurePassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Access token should be created successfully."""
        user_id = "test-user-id-123"
        token = create_access_token(subject=user_id)
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_access_token(self):
        """Valid access token should decode successfully."""
        user_id = "test-user-id-123"
        token = create_access_token(subject=user_id)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_access_token_with_additional_claims(self):
        """Access token with additional claims should include them."""
        user_id = "test-user-id-123"
        token = create_access_token(
            subject=user_id,
            additional_claims={"role": "admin", "company_id": "company-123"}
        )
        payload = decode_token(token)
        assert payload["role"] == "admin"
        assert payload["company_id"] == "company-123"

    def test_access_token_custom_expiry(self):
        """Access token with custom expiry should use that expiry."""
        user_id = "test-user-id-123"
        expires = timedelta(hours=2)
        token = create_access_token(subject=user_id, expires_delta=expires)
        payload = decode_token(token)
        # Check expiry is roughly 2 hours from now
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = exp - now
        assert timedelta(hours=1, minutes=59) < diff < timedelta(hours=2, minutes=1)

    def test_create_refresh_token(self):
        """Refresh token should be created successfully."""
        user_id = "test-user-id-123"
        token = create_refresh_token(subject=user_id)
        assert token is not None
        payload = decode_token(token)
        assert payload["type"] == "refresh"
        assert "jti" in payload  # Unique token ID

    def test_decode_invalid_token(self):
        """Invalid token should return None."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        assert payload is None

    def test_decode_expired_token(self):
        """Expired token should return None."""
        user_id = "test-user-id-123"
        # Create token that's already expired
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(seconds=-1)
        )
        payload = decode_token(token)
        assert payload is None


class TestPasswordResetToken:
    """Test password reset token functionality."""

    def test_generate_password_reset_token(self):
        """Password reset token should be generated."""
        email = "user@example.com"
        token = generate_password_reset_token(email)
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_password_reset_token(self):
        """Valid password reset token should return email."""
        email = "user@example.com"
        token = generate_password_reset_token(email)
        result = verify_password_reset_token(token)
        assert result == email

    def test_verify_invalid_password_reset_token(self):
        """Invalid password reset token should return None."""
        result = verify_password_reset_token("invalid.token")
        assert result is None


class TestDataEncryption:
    """Test sensitive data encryption/decryption."""

    def test_encrypt_decrypt_pan(self):
        """PAN should encrypt and decrypt correctly."""
        pan = "ABCDE1234F"
        encrypted = encrypt_sensitive_data(pan)
        assert encrypted != pan
        decrypted = decrypt_sensitive_data(encrypted)
        assert decrypted == pan

    def test_encrypt_decrypt_aadhaar(self):
        """Aadhaar should encrypt and decrypt correctly."""
        aadhaar = "123456789012"
        encrypted = encrypt_sensitive_data(aadhaar)
        assert encrypted != aadhaar
        decrypted = decrypt_sensitive_data(encrypted)
        assert decrypted == aadhaar

    def test_encrypt_decrypt_bank_account(self):
        """Bank account should encrypt and decrypt correctly."""
        account = "1234567890123456"
        encrypted = encrypt_sensitive_data(account)
        assert encrypted != account
        decrypted = decrypt_sensitive_data(encrypted)
        assert decrypted == account

    def test_encrypt_empty_string(self):
        """Empty string should return empty string."""
        result = encrypt_sensitive_data("")
        assert result == ""

    def test_decrypt_empty_string(self):
        """Empty string should return empty string."""
        result = decrypt_sensitive_data("")
        assert result == ""


class TestDataMasking:
    """Test sensitive data masking for display."""

    def test_mask_pan(self):
        """PAN should be masked correctly."""
        pan = "ABCDE1234F"
        masked = mask_pan(pan)
        assert masked == "ABCDE****F"

    def test_mask_pan_short(self):
        """Short PAN should return as-is."""
        pan = "ABC"
        masked = mask_pan(pan)
        assert masked == "ABC"

    def test_mask_aadhaar(self):
        """Aadhaar should be masked correctly."""
        aadhaar = "123456789012"
        masked = mask_aadhaar(aadhaar)
        assert masked == "XXXX-XXXX-9012"

    def test_mask_aadhaar_short(self):
        """Short Aadhaar should return as-is."""
        aadhaar = "123"
        masked = mask_aadhaar(aadhaar)
        assert masked == "123"

    def test_mask_bank_account(self):
        """Bank account should be masked correctly."""
        account = "1234567890"
        masked = mask_bank_account(account)
        assert masked == "XXXXXX7890"

    def test_mask_bank_account_short(self):
        """Short account should return as-is."""
        account = "123"
        masked = mask_bank_account(account)
        assert masked == "123"


class TestUserModel:
    """Test User model properties."""

    @pytest.mark.asyncio
    async def test_admin_user_is_admin(self, admin_user: User):
        """Admin user should have is_admin=True."""
        assert admin_user.is_admin is True

    @pytest.mark.asyncio
    async def test_admin_user_is_hr(self, admin_user: User):
        """Admin user should also have HR privileges."""
        assert admin_user.is_hr is True

    @pytest.mark.asyncio
    async def test_admin_user_is_accountant(self, admin_user: User):
        """Admin user should also have accountant privileges."""
        assert admin_user.is_accountant is True

    @pytest.mark.asyncio
    async def test_hr_user_is_hr(self, hr_user: User):
        """HR user should have is_hr=True."""
        assert hr_user.is_hr is True

    @pytest.mark.asyncio
    async def test_hr_user_not_admin(self, hr_user: User):
        """HR user should not be admin."""
        assert hr_user.is_admin is False

    @pytest.mark.asyncio
    async def test_employee_user_roles(self, employee_user: User):
        """Employee should only have employee privileges."""
        assert employee_user.is_admin is False
        assert employee_user.is_hr is False
        assert employee_user.is_accountant is False

    @pytest.mark.asyncio
    async def test_inactive_user_is_active(self, inactive_user: User):
        """Inactive user should have is_active=False."""
        assert inactive_user.is_active is False

    @pytest.mark.asyncio
    async def test_user_repr(self, admin_user: User):
        """User repr should show id, email, and role."""
        repr_str = repr(admin_user)
        assert "User" in repr_str
        assert admin_user.email in repr_str
        assert "admin" in repr_str
