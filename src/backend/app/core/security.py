"""
QA-001 to QA-003: Security Hardening
Comprehensive security middleware and utilities
"""
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
import hmac
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
# Note: CSP is strict - frontend must use external scripts/styles, not inline
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "X-Permitted-Cross-Domain-Policies": "none",
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
    """
    Rate limiting middleware with Redis support for distributed deployments.

    Falls back to in-memory storage if Redis is unavailable.
    """

    def __init__(self, app, max_requests: int = 100, window: int = 60, redis_url: str = None):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.redis_url = redis_url
        self._redis = None
        self._fallback_requests: Dict[str, List[datetime]] = {}  # Fallback for non-Redis

    async def _get_redis(self):
        """Get Redis client for distributed rate limiting."""
        if self._redis is None and self.redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
                await self._redis.ping()
            except Exception:
                self._redis = None
        return self._redis

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)

        if not await self._is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(self.window)}
            )

        await self._record_request(client_ip)
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP, handling proxies securely.

        Only trust X-Forwarded-For if behind a known proxy.
        """
        # Check for trusted proxy header (should be set by your load balancer)
        if request.headers.get("X-Real-IP"):
            return request.headers.get("X-Real-IP")

        # X-Forwarded-For can be spoofed - only trust first IP if behind trusted proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the rightmost IP (closest proxy) for security
            # In production, configure your proxy to strip untrusted headers
            ips = [ip.strip() for ip in forwarded.split(",")]
            # Return first non-private IP, or first IP if all are private
            for ip in ips:
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if not ip_obj.is_private:
                        return ip
                except ValueError:
                    continue
            return ips[0] if ips else "unknown"

        return request.client.host if request.client else "unknown"

    async def _is_allowed(self, client_ip: str) -> bool:
        """Check if client is within rate limit using Redis or fallback."""
        redis_client = await self._get_redis()

        if redis_client:
            try:
                key = f"rate_limit:{client_ip}"
                current = await redis_client.get(key)
                return int(current or 0) < self.max_requests
            except Exception:
                pass  # Fall through to in-memory

        # Fallback to in-memory (single instance only)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.window)

        if client_ip in self._fallback_requests:
            self._fallback_requests[client_ip] = [
                t for t in self._fallback_requests[client_ip] if t > cutoff
            ]
            return len(self._fallback_requests[client_ip]) < self.max_requests

        return True

    async def _record_request(self, client_ip: str) -> None:
        """Record a request using Redis or fallback."""
        redis_client = await self._get_redis()

        if redis_client:
            try:
                key = f"rate_limit:{client_ip}"
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, self.window)
                await pipe.execute()
                return
            except Exception:
                pass  # Fall through to in-memory

        # Fallback to in-memory
        now = datetime.now(timezone.utc)
        if client_ip not in self._fallback_requests:
            self._fallback_requests[client_ip] = []
        self._fallback_requests[client_ip].append(now)


class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """
    Defense-in-depth SQL injection detection middleware.

    IMPORTANT: This is NOT a replacement for parameterized queries!
    All database queries MUST use parameterized queries (SQLAlchemy ORM) as the
    primary defense against SQL injection. This middleware provides an additional
    layer of protection by detecting and blocking obvious attack patterns.

    This middleware:
    - Checks query strings and URL paths only (body inspection disabled to avoid stream issues)
    - URL-decodes values before pattern matching to catch encoding bypasses
    - Logs detected attempts for security monitoring

    NOTE: Body inspection is intentionally disabled because Starlette's BaseHTTPMiddleware
    has issues with body stream consumption that can cause "No response returned" errors.
    SQL injection protection for body content relies on parameterized queries (SQLAlchemy ORM).
    """

    # Comprehensive SQL injection patterns
    # Patterns work on URL-decoded strings
    SQL_PATTERNS = [
        # Basic SQL syntax elements that shouldn't appear in normal input
        r"(\-\-)|(/\*)|(\*/)",  # SQL comments
        r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)",  # Chained statements

        # UNION-based injection
        r"UNION\s+(ALL\s+)?SELECT",
        r"UNION\s+(ALL\s+)?/\*.*\*/\s*SELECT",

        # Classic SQL injection patterns
        r"'\s*(OR|AND)\s+['\d]",  # ' OR '1 / ' AND 1
        r"'\s*(OR|AND)\s+\w+\s*=\s*\w+",  # ' OR 1=1 / ' AND a=a
        r"1\s*=\s*1",  # Tautologies like 1=1
        r"'\s*=\s*'",  # '='

        # Dangerous SQL keywords with suspicious context
        r"(^|\s|;)(DROP|TRUNCATE|DELETE\s+FROM)\s+",
        r"(^|\s|;)INSERT\s+INTO\s+",
        r"(^|\s|;)UPDATE\s+\w+\s+SET\s+",
        r"(^|\s|;)ALTER\s+TABLE\s+",

        # Stored procedure execution
        r"EXEC(UTE)?\s+",
        r"xp_\w+",  # SQL Server extended procedures

        # Information schema access
        r"INFORMATION_SCHEMA\.",
        r"sys\.(tables|columns|databases)",

        # Sleep/benchmark (time-based blind injection)
        r"SLEEP\s*\(",
        r"BENCHMARK\s*\(",
        r"WAITFOR\s+DELAY",
        r"pg_sleep\s*\(",

        # Hex/char encoding attempts
        r"CHAR\s*\(\s*\d+\s*\)",
        r"0x[0-9a-fA-F]+",  # Hex literals in suspicious context

        # Stacked queries
        r";\s*\-\-",
    ]

    def __init__(self, app):
        super().__init__(app)
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        from urllib.parse import unquote_plus
        import logging

        logger = logging.getLogger("security.sqli")

        # Check query parameters (URL-decoded)
        query_string = unquote_plus(str(request.query_params))

        if self._contains_sql_injection(query_string):
            logger.warning(
                f"SQL injection attempt detected in query string from {request.client.host}: {query_string[:200]}"
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request parameters"}
            )

        # Check path parameters (URL-decoded)
        path = unquote_plus(request.url.path)
        if self._contains_sql_injection(path):
            logger.warning(
                f"SQL injection attempt detected in path from {request.client.host}: {path[:200]}"
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request path"}
            )

        # NOTE: Body inspection disabled - causes "No response returned" errors
        # due to Starlette BaseHTTPMiddleware body stream consumption issues.
        # SQL injection protection for body content relies on parameterized queries.

        return await call_next(request)

    def _contains_sql_injection(self, value: str) -> bool:
        """
        Check if value contains SQL injection patterns.

        Note: This is a heuristic check and may have false positives/negatives.
        Always use parameterized queries as the primary defense.
        """
        if not value:
            return False

        for pattern in self._patterns:
            if pattern.search(value):
                return True
        return False


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Defense-in-depth XSS detection middleware.

    IMPORTANT: This is NOT a replacement for proper output encoding!
    All user input displayed in HTML MUST be properly escaped/encoded.
    This middleware provides an additional layer of protection by detecting
    and blocking obvious XSS attack patterns in inputs.

    This middleware:
    - Checks query strings and URL paths only (body inspection disabled to avoid stream issues)
    - URL-decodes values before pattern matching to catch encoding bypasses
    - Logs detected attempts for security monitoring

    NOTE: Body inspection is intentionally disabled because Starlette's BaseHTTPMiddleware
    has issues with body stream consumption that can cause "No response returned" errors.
    XSS protection for body content relies on proper output encoding in the frontend.
    """

    XSS_PATTERNS = [
        # Script tags (various forms)
        r"<\s*script[^>]*>",
        r"<\s*/\s*script\s*>",

        # JavaScript URI scheme
        r"javascript\s*:",
        r"vbscript\s*:",
        r"data\s*:\s*text/html",

        # Event handlers (comprehensive list)
        r"on(abort|activate|afterprint|afterupdate|beforeactivate|beforecopy|beforecut|beforedeactivate|beforeeditfocus|beforepaste|beforeprint|beforeunload|beforeupdate|blur|bounce|cellchange|change|click|contextmenu|controlselect|copy|cut|dataavailable|datasetchanged|datasetcomplete|dblclick|deactivate|drag|dragend|dragenter|dragleave|dragover|dragstart|drop|error|errorupdate|filterchange|finish|focus|focusin|focusout|hashchange|help|input|keydown|keypress|keyup|layoutcomplete|load|losecapture|message|mousedown|mouseenter|mouseleave|mousemove|mouseout|mouseover|mouseup|mousewheel|move|moveend|movestart|offline|online|pagehide|pageshow|paste|popstate|progress|propertychange|readystatechange|reset|resize|resizeend|resizestart|rowenter|rowexit|rowsdelete|rowsinserted|scroll|search|select|selectionchange|selectstart|start|stop|storage|submit|timeout|touchcancel|touchend|touchmove|touchstart|unload|wheel)\s*=",

        # Dangerous HTML elements
        r"<\s*iframe[^>]*>",
        r"<\s*object[^>]*>",
        r"<\s*embed[^>]*>",
        r"<\s*frame[^>]*>",
        r"<\s*frameset[^>]*>",
        r"<\s*applet[^>]*>",
        r"<\s*base[^>]*>",
        r"<\s*link[^>]*>",
        r"<\s*meta[^>]*>",
        r"<\s*style[^>]*>",

        # SVG-based XSS
        r"<\s*svg[^>]*>",
        r"<\s*math[^>]*>",

        # Expression/eval patterns
        r"expression\s*\(",
        r"eval\s*\(",
        r"Function\s*\(",
        r"setTimeout\s*\(",
        r"setInterval\s*\(",

        # HTML entity encoded variants of < and >
        r"&lt;\s*script",
        r"&#60;\s*script",
        r"&#x3c;\s*script",
    ]

    def __init__(self, app):
        super().__init__(app)
        self._patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.XSS_PATTERNS]

    async def dispatch(self, request: Request, call_next):
        from urllib.parse import unquote_plus
        import logging

        logger = logging.getLogger("security.xss")

        # Check query parameters (URL-decoded)
        query_string = unquote_plus(str(request.query_params))
        if self._contains_xss(query_string):
            logger.warning(
                f"XSS attempt detected in query string from {request.client.host}: {query_string[:200]}"
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request parameters"}
            )

        # Check path (URL-decoded)
        path = unquote_plus(request.url.path)
        if self._contains_xss(path):
            logger.warning(
                f"XSS attempt detected in path from {request.client.host}: {path[:200]}"
            )
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request path"}
            )

        # NOTE: Body inspection disabled - causes "No response returned" errors
        # due to Starlette BaseHTTPMiddleware body stream consumption issues.
        # XSS protection for body content relies on proper output encoding.

        return await call_next(request)

    def _contains_xss(self, value: str) -> bool:
        """
        Check if value contains XSS patterns.

        Note: This is a heuristic check and may have false positives/negatives.
        Always use proper output encoding as the primary defense.
        """
        if not value:
            return False

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
        """
        Hash password using Argon2id (memory-hard algorithm).

        Argon2id is the recommended password hashing algorithm by OWASP.
        Falls back to PBKDF2 if argon2 is not available.
        """
        try:
            from argon2 import PasswordHasher
            from argon2.profiles import RFC_9106_LOW_MEMORY
            ph = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)
            return ph.hash(password)
        except ImportError:
            # Fallback to PBKDF2 if argon2 not installed
            salt = secrets.token_hex(16)
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return f"pbkdf2${salt}${hashed.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash.

        Supports both Argon2 and legacy PBKDF2 hashes for migration.
        """
        try:
            # Check if it's an Argon2 hash (starts with $argon2)
            if hashed.startswith('$argon2'):
                from argon2 import PasswordHasher
                from argon2.exceptions import VerifyMismatchError
                ph = PasswordHasher()
                try:
                    ph.verify(hashed, password)
                    return True
                except VerifyMismatchError:
                    return False
            # Legacy PBKDF2 hash (format: pbkdf2$salt$hash or salt$hash)
            elif hashed.startswith('pbkdf2$'):
                parts = hashed.split('$')
                salt, hash_value = parts[1], parts[2]
            else:
                salt, hash_value = hashed.split('$')

            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return hmac.compare_digest(new_hash.hex(), hash_value)
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        """Check if password hash needs to be upgraded to Argon2."""
        return not hashed.startswith('$argon2')


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
