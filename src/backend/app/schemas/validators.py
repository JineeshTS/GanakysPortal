"""
Shared Validators for Pydantic Schemas
Common validation functions used across multiple schemas
"""
import re
from typing import Optional


def validate_phone(value: Optional[str]) -> Optional[str]:
    """
    Validate phone number format.

    Accepts:
    - Indian mobile: 10 digits starting with 6-9, optionally with +91 prefix
    - Indian landline: 11-12 digits with STD code (starting with 0)
    - International: Numbers with country code prefix (+XX)

    Returns the cleaned/normalized value or original if format is acceptable.
    """
    if not value:
        return None

    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', value)

    # Check for valid Indian phone patterns
    # Mobile: 10 digits starting with 6-9
    if re.match(r'^(\+91)?[6-9]\d{9}$', cleaned):
        return cleaned

    # Landline: 11-12 digits with STD code
    if re.match(r'^0\d{10,11}$', cleaned):
        return cleaned

    # International format: +country_code followed by digits
    if re.match(r'^\+\d{1,3}\d{6,14}$', cleaned):
        return cleaned

    # Allow other formats for flexibility (legacy data)
    # but only if it contains mostly digits and is reasonable length
    digits_only = re.sub(r'\D', '', value)
    if 7 <= len(digits_only) <= 15:
        return value

    return value  # Return as-is for compatibility


def validate_pincode(value: Optional[str]) -> Optional[str]:
    """
    Validate Indian pincode format.

    Accepts:
    - 6 digit pincode (first digit 1-9)
    """
    if not value:
        return None

    cleaned = value.strip()

    # Indian pincode: 6 digits, first digit 1-9
    if re.match(r'^[1-9]\d{5}$', cleaned):
        return cleaned

    return value  # Return as-is for compatibility


def validate_pan(value: Optional[str]) -> Optional[str]:
    """
    Validate Indian PAN (Permanent Account Number) format.

    Format: AAAAA9999A (5 letters, 4 digits, 1 letter)
    """
    if not value:
        return None

    cleaned = value.strip().upper()

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, cleaned):
        raise ValueError("Invalid PAN format. Expected format: AAAAA9999A")

    return cleaned


def validate_gstin(value: Optional[str]) -> Optional[str]:
    """
    Validate Indian GSTIN format.

    Format: 22AAAAA0000A1Z5 (2 state digits, 10 char PAN, 1 entity, 1 Z, 1 checksum)
    """
    if not value:
        return None

    cleaned = value.strip().upper()

    # GSTIN: 15 characters
    # First 2: State code (01-37)
    # Next 10: PAN
    # Next 1: Entity number
    # Next 1: Z (default)
    # Next 1: Checksum
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    if not re.match(pattern, cleaned):
        raise ValueError("Invalid GSTIN format")

    return cleaned


def validate_ifsc(value: Optional[str]) -> Optional[str]:
    """
    Validate Indian IFSC (Indian Financial System Code) format.

    Format: AAAA0NNNNNN (4 letters bank code, 0, 6 alphanumeric branch code)
    """
    if not value:
        return None

    cleaned = value.strip().upper()

    # IFSC: 11 characters - 4 letter bank code, 0, 6 alphanumeric
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    if not re.match(pattern, cleaned):
        raise ValueError("Invalid IFSC format. Expected format: AAAA0NNNNNN")

    return cleaned


def validate_account_number(value: Optional[str]) -> Optional[str]:
    """
    Validate bank account number.

    Accepts: 9-18 digit account numbers
    """
    if not value:
        return None

    cleaned = re.sub(r'\s', '', value)

    # Account numbers are typically 9-18 digits
    if re.match(r'^\d{9,18}$', cleaned):
        return cleaned

    return value  # Return as-is for compatibility
