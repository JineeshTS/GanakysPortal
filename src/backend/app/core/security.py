"""
QA-001 to QA-003: Security Hardening
Comprehensive security middleware and utilities
"""
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import re
import ipaddress
from enum import Enum

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware


# =============================================================================
# Security Constants
# =============================================================================

class SecurityLevel(str, Enum):
    """Security levels for endpoints."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# OWASP Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# Rate limiting defaults
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100


# =============================================================================
# Security Middleware
# =============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._requests: Dict[str, List[datetime]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)

        if not self._is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(self.window)}
            )

        self._record_request(client_ip)
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, handling proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_allowed(self, client_ip: str) -> bool:
        """Check if client is within rate limit."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window)

        if client_ip in self._requests:
            # Clean old requests
            self._requests[client_ip] = [
                t for t in self._requests[client_ip] if t > cutoff
            ]
            return len(self._requests[client_ip]) < self.max_requests

        return True

    def _record_request(self, client_ip: str) -> None:
        """Record a request from client."""
        now = datetime.utcnow()
        if client_ip not in self._requests:
            self._requests[client_ip] = []
        self._requests[client_ip].append(now)


class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """Detect and block SQL injection attempts."""

    SQL_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
        r"UNION\s+SELECT",
        r"INSERT\s+INTO",
        r"DELETE\s+FROM",
        r"DROP\s+TABLE",
        r"UPDATE\s+\w+\s+SET",
    ]

    def __init__(self, app):
        super().__init__(app)
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        # Check query parameters
        query_string = str(request.query_params)
        if self._contains_sql_injection(query_string):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request parameters"
            )

        # Check path parameters
        path = request.url.path
        if self._contains_sql_injection(path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request path"
            )

        return await call_next(request)

    def _contains_sql_injection(self, value: str) -> bool:
        """Check if value contains SQL injection patterns."""
        for pattern in self._patterns:
            if pattern.search(value):
                return True
        return False


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Detect and sanitize XSS attempts."""

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<svg[^>]*onload",
    ]

    def __init__(self, app):
        super().__init__(app)
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        query_string = str(request.query_params)

        if self._contains_xss(query_string):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request parameters"
            )

        return await call_next(request)

    def _contains_xss(self, value: str) -> bool:
        """Check if value contains XSS patterns."""
        for pattern in self._patterns:
            if pattern.search(value):
                return True
        return False


# =============================================================================
# Input Validation
# =============================================================================

class InputValidator:
    """Validate and sanitize user inputs."""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not value:
            return ""

        # Truncate to max length
        value = value[:max_length]

        # Remove null bytes
        value = value.replace("\x00", "")

        # Escape HTML entities
        html_escape = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
        }
        for char, escape in html_escape.items():
            value = value.replace(char, escape)

        return value

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Indian phone number."""
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', phone)
        # Check for 10-digit number or with country code
        pattern = r'^(\+91)?[6-9]\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_pan(pan: str) -> bool:
        """Validate PAN number format."""
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        return bool(re.match(pattern, pan.upper()))

    @staticmethod
    def validate_gstin(gstin: str) -> bool:
        """Validate GSTIN format."""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        return bool(re.match(pattern, gstin.upper()))

    @staticmethod
    def validate_aadhaar(aadhaar: str) -> bool:
        """Validate Aadhaar number format."""
        aadhaar = re.sub(r'[\s\-]', '', aadhaar)
        return len(aadhaar) == 12 and aadhaar.isdigit()

    @staticmethod
    def validate_ifsc(ifsc: str) -> bool:
        """Validate IFSC code format."""
        pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
        return bool(re.match(pattern, ifsc.upper()))

    @staticmethod
    def validate_account_number(account: str) -> bool:
        """Validate bank account number."""
        account = re.sub(r'[\s\-]', '', account)
        return 9 <= len(account) <= 18 and account.isdigit()


# =============================================================================
# Password Security
# =============================================================================

class PasswordPolicy:
    """Password policy enforcement."""

    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Common passwords to reject
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "password1", "admin", "letmein", "welcome", "monkey",
        "dragon", "master", "login", "password123", "admin123",
    }

    @classmethod
    def validate(cls, password: str) -> tuple[bool, List[str]]:
        """Validate password against policy."""
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_LENGTH} characters")

        if len(password) > cls.MAX_LENGTH:
            errors.append(f"Password must not exceed {cls.MAX_LENGTH} characters")

        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")

        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")

        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")

        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            errors.append("Password must contain at least one special character")

        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("Password is too common")

        return len(errors) == 0, errors

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using secure algorithm."""
        # In production, use bcrypt or argon2
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return f"{salt}${hashed.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_value = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return new_hash.hex() == hash_value
        except Exception:
            return False


# =============================================================================
# Data Masking
# =============================================================================

class DataMasker:
    """Mask sensitive data in responses."""

    @staticmethod
    def mask_pan(pan: str) -> str:
        """Mask PAN number: ABCPK1234A -> XXXXX1234X"""
        if not pan or len(pan) != 10:
            return pan
        return f"XXXXX{pan[5:9]}X"

    @staticmethod
    def mask_aadhaar(aadhaar: str) -> str:
        """Mask Aadhaar: 123456789012 -> XXXX-XXXX-9012"""
        aadhaar = re.sub(r'[\s\-]', '', aadhaar)
        if not aadhaar or len(aadhaar) != 12:
            return aadhaar
        return f"XXXX-XXXX-{aadhaar[-4:]}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone: 9876543210 -> XXXXXX3210"""
        phone = re.sub(r'[\s\-]', '', phone)
        if len(phone) < 4:
            return phone
        return f"{'X' * (len(phone) - 4)}{phone[-4:]}"

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email: user@domain.com -> u***@domain.com"""
        if '@' not in email:
            return email
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*'
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_account_number(account: str) -> str:
        """Mask bank account: 1234567890123456 -> XXXXXXXXXXXX3456"""
        if len(account) <= 4:
            return account
        return 'X' * (len(account) - 4) + account[-4:]

    @staticmethod
    def mask_dict(data: Dict[str, Any], fields_to_mask: List[str]) -> Dict[str, Any]:
        """Mask specified fields in dictionary."""
        masked = data.copy()

        field_maskers = {
            'pan': DataMasker.mask_pan,
            'aadhaar': DataMasker.mask_aadhaar,
            'phone': DataMasker.mask_phone,
            'mobile': DataMasker.mask_phone,
            'email': DataMasker.mask_email,
            'account_number': DataMasker.mask_account_number,
        }

        for field in fields_to_mask:
            if field in masked and masked[field]:
                masker = field_maskers.get(field, lambda x: 'XXXX')
                masked[field] = masker(str(masked[field]))

        return masked


# =============================================================================
# CSRF Protection
# =============================================================================

class CSRFProtection:
    """CSRF token management."""

    TOKEN_LENGTH = 32
    TOKEN_HEADER = "X-CSRF-Token"
    TOKEN_COOKIE = "csrf_token"

    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(CSRFProtection.TOKEN_LENGTH)

    @staticmethod
    def validate_token(request_token: str, session_token: str) -> bool:
        """Validate CSRF token."""
        if not request_token or not session_token:
            return False
        return secrets.compare_digest(request_token, session_token)


# =============================================================================
# IP Whitelist/Blacklist
# =============================================================================

class IPFilter:
    """IP address filtering."""

    def __init__(self):
        self.whitelist: List[str] = []
        self.blacklist: List[str] = []

    def add_to_whitelist(self, ip: str) -> None:
        """Add IP to whitelist."""
        self.whitelist.append(ip)

    def add_to_blacklist(self, ip: str) -> None:
        """Add IP to blacklist."""
        self.blacklist.append(ip)

    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed."""
        # If whitelist is set, only allow whitelisted IPs
        if self.whitelist:
            return self._ip_in_list(ip, self.whitelist)

        # Otherwise, block blacklisted IPs
        return not self._ip_in_list(ip, self.blacklist)

    def _ip_in_list(self, ip: str, ip_list: List[str]) -> bool:
        """Check if IP is in list (supports CIDR notation)."""
        try:
            client_ip = ipaddress.ip_address(ip)
            for entry in ip_list:
                if '/' in entry:
                    network = ipaddress.ip_network(entry, strict=False)
                    if client_ip in network:
                        return True
                elif ip == entry:
                    return True
        except ValueError:
            pass
        return False
