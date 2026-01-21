#!/usr/bin/env python3
"""
Test script for security changes:
- Encryption (AES-256-GCM)
- Password hashing (Argon2)
- Token management (JWT)
- Secrets manager
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_encryption():
    """Test AES-256-GCM encryption/decryption"""
    print("\n=== Testing Encryption (AES-256-GCM) ===")

    from app.core.encryption import EncryptionService

    encryption = EncryptionService(master_key="test-master-key-for-encryption-32")

    # Test basic encryption/decryption
    test_data = [
        "Hello, World!",
        "Sensitive PAN: ABCDE1234F",
        "Bank Account: 1234567890123456",
        "Special chars: @#$%^&*()_+={}[]|\\:\";<>?,./`~",
        "Unicode: नमस्ते 你好 مرحبا",
        "",  # Empty string
    ]

    passed = 0
    failed = 0

    for plaintext in test_data:
        try:
            encrypted = encryption.encrypt(plaintext)
            decrypted = encryption.decrypt(encrypted)

            if decrypted == plaintext:
                print(f"  ✓ Encrypt/Decrypt: '{plaintext[:30]}...' OK")
                passed += 1
            else:
                print(f"  ✗ Encrypt/Decrypt MISMATCH: '{plaintext[:30]}...'")
                failed += 1
        except Exception as e:
            print(f"  ✗ Encrypt/Decrypt ERROR: '{plaintext[:30]}...' - {e}")
            failed += 1

    # Test that encrypted data is different each time (due to random nonce)
    encrypted1 = encryption.encrypt("same data")
    encrypted2 = encryption.encrypt("same data")
    if encrypted1 != encrypted2:
        print("  ✓ Random nonce: Same plaintext produces different ciphertext")
        passed += 1
    else:
        print("  ✗ Random nonce: Same plaintext produced same ciphertext!")
        failed += 1

    # Test tamper detection
    try:
        tampered = encrypted1[:-10] + "XXXXXXXXXX"
        encryption.decrypt(tampered)
        print("  ✗ Tamper detection: Failed to detect tampering!")
        failed += 1
    except ValueError:
        print("  ✓ Tamper detection: Correctly rejected tampered data")
        passed += 1

    print(f"\nEncryption tests: {passed} passed, {failed} failed")
    return failed == 0


def test_password_hashing():
    """Test Argon2 password hashing"""
    print("\n=== Testing Password Hashing (Argon2) ===")

    from app.core.security import PasswordPolicy as PasswordUtils

    passed = 0
    failed = 0

    # Test password hashing
    passwords = [
        "simple",
        "P@ssw0rd!",
        "very-long-password-with-special-chars-!@#$%^&*()",
        "Unicode: पासवर्ड 密码",
    ]

    for password in passwords:
        try:
            hashed = PasswordUtils.hash_password(password)

            # Check hash format (Argon2 starts with $argon2)
            if hashed.startswith("$argon2"):
                print(f"  ✓ Hash format: Argon2 format detected for '{password[:20]}...'")
                passed += 1
            else:
                print(f"  ✗ Hash format: Not Argon2 format for '{password[:20]}...'")
                failed += 1

            # Verify password
            if PasswordUtils.verify_password(password, hashed):
                print(f"  ✓ Verification: Correct password verified")
                passed += 1
            else:
                print(f"  ✗ Verification: Failed to verify correct password")
                failed += 1

            # Verify wrong password is rejected
            if not PasswordUtils.verify_password("wrong-password", hashed):
                print(f"  ✓ Rejection: Wrong password rejected")
                passed += 1
            else:
                print(f"  ✗ Rejection: Wrong password was accepted!")
                failed += 1

        except Exception as e:
            print(f"  ✗ ERROR for '{password[:20]}...': {e}")
            failed += 1

    # Test needs_rehash function
    try:
        # Argon2 hash should not need rehash
        argon2_hash = PasswordUtils.hash_password("test")
        if not PasswordUtils.needs_rehash(argon2_hash):
            print("  ✓ needs_rehash: Argon2 hash does not need rehash")
            passed += 1
        else:
            print("  ✗ needs_rehash: Argon2 hash incorrectly flagged for rehash")
            failed += 1

        # PBKDF2 hash should need rehash
        pbkdf2_hash = "pbkdf2$salt$hashvalue"
        if PasswordUtils.needs_rehash(pbkdf2_hash):
            print("  ✓ needs_rehash: PBKDF2 hash flagged for rehash")
            passed += 1
        else:
            print("  ✗ needs_rehash: PBKDF2 hash not flagged for rehash")
            failed += 1
    except Exception as e:
        print(f"  ✗ needs_rehash ERROR: {e}")
        failed += 1

    print(f"\nPassword hashing tests: {passed} passed, {failed} failed")
    return failed == 0


def test_token_manager():
    """Test JWT token management"""
    print("\n=== Testing Token Manager (JWT) ===")

    from app.core.encryption import TokenManager

    token_manager = TokenManager(secret_key="test-secret-key-for-jwt-tokens")

    passed = 0
    failed = 0

    # Test access token creation and verification
    try:
        access_token = token_manager.create_access_token(
            user_id="user-123",
            email="test@example.com",
            role="admin",
            company_id="company-456"
        )

        payload = token_manager.verify_token(access_token, "access")

        if payload and payload.get("sub") == "user-123":
            print("  ✓ Access token: Created and verified")
            passed += 1
        else:
            print("  ✗ Access token: Verification failed")
            failed += 1

        # Check token claims
        if payload.get("email") == "test@example.com":
            print("  ✓ Token claims: Email claim present")
            passed += 1
        else:
            print("  ✗ Token claims: Email claim missing")
            failed += 1

    except Exception as e:
        print(f"  ✗ Access token ERROR: {e}")
        failed += 1

    # Test refresh token
    try:
        refresh_token = token_manager.create_refresh_token(user_id="user-123")
        payload = token_manager.verify_token(refresh_token, "refresh")

        if payload and payload.get("type") == "refresh":
            print("  ✓ Refresh token: Created and verified")
            passed += 1
        else:
            print("  ✗ Refresh token: Verification failed")
            failed += 1
    except Exception as e:
        print(f"  ✗ Refresh token ERROR: {e}")
        failed += 1

    # Test token blacklisting
    try:
        token_manager.blacklist_token(access_token)
        if token_manager.is_blacklisted(access_token):
            print("  ✓ Blacklisting: Token blacklisted")
            passed += 1
        else:
            print("  ✗ Blacklisting: Token not blacklisted")
            failed += 1

        # Blacklisted token should not verify
        if token_manager.verify_token(access_token, "access") is None:
            print("  ✓ Blacklisted verification: Blacklisted token rejected")
            passed += 1
        else:
            print("  ✗ Blacklisted verification: Blacklisted token accepted!")
            failed += 1
    except Exception as e:
        print(f"  ✗ Blacklisting ERROR: {e}")
        failed += 1

    # Test password reset token
    try:
        reset_token = token_manager.create_password_reset_token(
            user_id="user-123",
            email="test@example.com"
        )
        payload = token_manager.verify_token(reset_token, "password_reset")

        if payload and payload.get("type") == "password_reset":
            print("  ✓ Password reset token: Created and verified")
            passed += 1
        else:
            print("  ✗ Password reset token: Verification failed")
            failed += 1
    except Exception as e:
        print(f"  ✗ Password reset token ERROR: {e}")
        failed += 1

    # Verify token expiry setting (should be 15 minutes)
    if token_manager.ACCESS_TOKEN_EXPIRE_MINUTES == 15:
        print("  ✓ Token expiry: Access token expires in 15 minutes")
        passed += 1
    else:
        print(f"  ✗ Token expiry: Expected 15, got {token_manager.ACCESS_TOKEN_EXPIRE_MINUTES}")
        failed += 1

    print(f"\nToken manager tests: {passed} passed, {failed} failed")
    return failed == 0


def test_secrets_manager():
    """Test secrets manager"""
    print("\n=== Testing Secrets Manager ===")

    # Set test environment variables with production-like values (no insecure patterns)
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['JWT_SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'  # 32 chars, no insecure patterns
    os.environ['ENCRYPTION_KEY'] = 'q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2'  # 32 chars, no insecure patterns
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://user:mydbpass123@localhost:5432/ganaportal'

    # Force reload of the singleton
    from app.core import secrets
    import importlib
    importlib.reload(secrets)

    from app.core.secrets import SecretsManager

    passed = 0
    failed = 0

    # Create fresh instance
    SecretsManager._instance = None
    SecretsManager._initialized = False
    sm = SecretsManager()

    # Test JWT secret key retrieval
    try:
        jwt_key = sm.jwt_secret_key
        if jwt_key == 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6':
            print("  ✓ JWT secret key: Retrieved from environment")
            passed += 1
        else:
            print(f"  ✗ JWT secret key: Unexpected value")
            failed += 1
    except Exception as e:
        print(f"  ✗ JWT secret key ERROR: {e}")
        failed += 1

    # Test encryption key retrieval
    try:
        enc_key = sm.encryption_key
        if enc_key == 'q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2':
            print("  ✓ Encryption key: Retrieved from environment")
            passed += 1
        else:
            print(f"  ✗ Encryption key: Unexpected value")
            failed += 1
    except Exception as e:
        print(f"  ✗ Encryption key ERROR: {e}")
        failed += 1

    # Test secret masking
    try:
        masked = sm.mask_secret("this-is-a-long-secret-value")
        if masked == "this...alue":
            print("  ✓ Secret masking: Correctly masked")
            passed += 1
        else:
            print(f"  ✗ Secret masking: Got '{masked}'")
            failed += 1
    except Exception as e:
        print(f"  ✗ Secret masking ERROR: {e}")
        failed += 1

    # Test short secret masking
    try:
        masked_short = sm.mask_secret("short")
        if masked_short == "***":
            print("  ✓ Short secret masking: Correctly masked as ***")
            passed += 1
        else:
            print(f"  ✗ Short secret masking: Got '{masked_short}'")
            failed += 1
    except Exception as e:
        print(f"  ✗ Short secret masking ERROR: {e}")
        failed += 1

    # Test production validation
    try:
        errors = sm.validate_production_secrets()
        # Should have no errors since we set valid secrets
        if len(errors) == 0:
            print("  ✓ Production validation: No errors with valid secrets")
            passed += 1
        else:
            print(f"  ✗ Production validation: Got errors: {errors}")
            failed += 1
    except Exception as e:
        print(f"  ✗ Production validation ERROR: {e}")
        failed += 1

    print(f"\nSecrets manager tests: {passed} passed, {failed} failed")
    return failed == 0


def test_field_level_encryption():
    """Test field-level encryption for sensitive data"""
    print("\n=== Testing Field-Level Encryption ===")

    from app.core.encryption import EncryptionService, FieldLevelEncryption

    encryption_service = EncryptionService(master_key="test-master-key-for-encryption-32")
    field_encryption = FieldLevelEncryption(encryption_service)

    passed = 0
    failed = 0

    # Test data with sensitive fields
    test_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "pan": "ABCDE1234F",
        "aadhaar": "123456789012",
        "account_number": "1234567890123456",
        "salary": "50000",
    }

    try:
        # Encrypt sensitive fields
        encrypted_data = field_encryption.encrypt_model_fields(test_data)

        # Check non-sensitive fields are unchanged
        if encrypted_data["name"] == "John Doe" and encrypted_data["email"] == "john@example.com":
            print("  ✓ Non-sensitive fields: Unchanged after encryption")
            passed += 1
        else:
            print("  ✗ Non-sensitive fields: Were modified!")
            failed += 1

        # Check sensitive fields are encrypted (different from original)
        if encrypted_data["pan"] != "ABCDE1234F":
            print("  ✓ PAN field: Encrypted")
            passed += 1
        else:
            print("  ✗ PAN field: Not encrypted!")
            failed += 1

        if encrypted_data["aadhaar"] != "123456789012":
            print("  ✓ Aadhaar field: Encrypted")
            passed += 1
        else:
            print("  ✗ Aadhaar field: Not encrypted!")
            failed += 1

        # Decrypt and verify
        decrypted_data = field_encryption.decrypt_model_fields(encrypted_data)

        if decrypted_data["pan"] == "ABCDE1234F":
            print("  ✓ PAN decryption: Correct")
            passed += 1
        else:
            print(f"  ✗ PAN decryption: Got '{decrypted_data['pan']}'")
            failed += 1

        if decrypted_data["salary"] == "50000":
            print("  ✓ Salary decryption: Correct")
            passed += 1
        else:
            print(f"  ✗ Salary decryption: Got '{decrypted_data['salary']}'")
            failed += 1

    except Exception as e:
        print(f"  ✗ Field encryption ERROR: {e}")
        failed += 1

    print(f"\nField-level encryption tests: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all security tests"""
    print("=" * 60)
    print("SECURITY CHANGES TEST SUITE")
    print("=" * 60)

    results = []

    results.append(("Encryption (AES-256-GCM)", test_encryption()))
    results.append(("Password Hashing (Argon2)", test_password_hashing()))
    results.append(("Token Manager (JWT)", test_token_manager()))
    results.append(("Secrets Manager", test_secrets_manager()))
    results.append(("Field-Level Encryption", test_field_level_encryption()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ ALL SECURITY TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
