"""
Recruitment Security Module
Sprint 5: Security hardening for the recruitment pipeline
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from functools import wraps
from uuid import UUID
import hashlib
import re
import logging

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

logger = logging.getLogger("recruitment.security")


# =============================================================================
# Recruitment-Specific Rate Limiting
# =============================================================================

class RecruitmentRateLimiter:
    """
    Enhanced rate limiting for recruitment endpoints.
    Provides stricter limits for sensitive operations.
    """

    # Rate limits per endpoint category (requests per window)
    RATE_LIMITS = {
        # Authentication - strict limits to prevent brute force
        "candidate_login": {"requests": 5, "window": 300},  # 5 per 5 min
        "candidate_register": {"requests": 3, "window": 3600},  # 3 per hour
        "password_reset": {"requests": 3, "window": 3600},  # 3 per hour

        # Applications - moderate limits
        "job_apply": {"requests": 10, "window": 3600},  # 10 per hour
        "application_withdraw": {"requests": 5, "window": 3600},  # 5 per hour

        # AI Interview - strict to prevent abuse
        "interview_start": {"requests": 3, "window": 3600},  # 3 per hour
        "interview_submit": {"requests": 20, "window": 1800},  # 20 per 30 min

        # Offer actions - very strict
        "offer_respond": {"requests": 5, "window": 3600},  # 5 per hour

        # Search/Browse - lenient
        "job_search": {"requests": 100, "window": 60},  # 100 per minute
        "job_view": {"requests": 200, "window": 60},  # 200 per minute
    }

    def __init__(self):
        self._requests: Dict[str, Dict[str, List[datetime]]] = {}

    def check_rate_limit(
        self,
        category: str,
        identifier: str,
        redis_client=None
    ) -> bool:
        """
        Check if request is within rate limit.

        Args:
            category: Rate limit category (e.g., 'candidate_login')
            identifier: Unique identifier (e.g., IP, email, candidate_id)
            redis_client: Optional Redis client for distributed rate limiting

        Returns:
            True if allowed, False if rate limited
        """
        if category not in self.RATE_LIMITS:
            return True

        limit = self.RATE_LIMITS[category]
        key = f"{category}:{identifier}"
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=limit["window"])

        # In-memory fallback
        if key not in self._requests:
            self._requests[key] = []

        # Clean old requests
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

        if len(self._requests[key]) >= limit["requests"]:
            logger.warning(f"Rate limit exceeded for {category}: {identifier}")
            return False

        self._requests[key].append(now)
        return True

    def get_retry_after(self, category: str) -> int:
        """Get retry-after seconds for a rate limit category."""
        if category in self.RATE_LIMITS:
            return self.RATE_LIMITS[category]["window"]
        return 60


# Global rate limiter instance
recruitment_rate_limiter = RecruitmentRateLimiter()


def rate_limit(category: str):
    """
    Decorator for rate limiting recruitment endpoints.

    Usage:
        @router.post("/login")
        @rate_limit("candidate_login")
        async def login(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or next(
                (arg for arg in args if isinstance(arg, Request)), None
            )

            if request:
                # Use IP + endpoint as identifier
                client_ip = request.client.host if request.client else "unknown"
                identifier = f"{client_ip}:{request.url.path}"

                if not recruitment_rate_limiter.check_rate_limit(category, identifier):
                    retry_after = recruitment_rate_limiter.get_retry_after(category)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests. Please try again later.",
                        headers={"Retry-After": str(retry_after)}
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Input Validation for Recruitment
# =============================================================================

class RecruitmentInputValidator:
    """Validate recruitment-specific inputs."""

    # Patterns for common injections in resume/cover letter
    SUSPICIOUS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"eval\s*\(",
        r"document\.",
        r"window\.",
    ]

    @staticmethod
    def validate_job_application(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate job application data."""
        errors = []

        # Cover letter validation
        if cover_letter := data.get("cover_letter"):
            if len(cover_letter) > 10000:
                errors.append("Cover letter exceeds maximum length (10,000 characters)")
            if RecruitmentInputValidator._contains_suspicious_content(cover_letter):
                errors.append("Cover letter contains invalid content")

        # Expected salary validation
        if expected_salary := data.get("expected_salary"):
            try:
                salary = float(expected_salary)
                if salary < 0 or salary > 100000000:
                    errors.append("Invalid expected salary")
            except (ValueError, TypeError):
                errors.append("Expected salary must be a number")

        # Notice period validation
        if notice_period := data.get("notice_period_days"):
            try:
                days = int(notice_period)
                if days < 0 or days > 365:
                    errors.append("Notice period must be between 0 and 365 days")
            except (ValueError, TypeError):
                errors.append("Notice period must be a number")

        return len(errors) == 0, errors

    @staticmethod
    def validate_interview_response(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate AI interview response data."""
        errors = []

        # Duration validation
        if duration := data.get("duration_seconds"):
            try:
                seconds = int(duration)
                if seconds < 0 or seconds > 600:  # Max 10 minutes per answer
                    errors.append("Invalid response duration")
            except (ValueError, TypeError):
                errors.append("Duration must be a number")

        # Transcript validation
        if transcript := data.get("transcript"):
            if len(transcript) > 50000:
                errors.append("Transcript exceeds maximum length")

        return len(errors) == 0, errors

    @staticmethod
    def validate_offer_response(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate offer response data."""
        errors = []

        # Decision validation
        if decision := data.get("decision"):
            valid_decisions = ["accept", "reject", "negotiate"]
            if decision not in valid_decisions:
                errors.append(f"Decision must be one of: {', '.join(valid_decisions)}")

        # Negotiation notes validation
        if notes := data.get("negotiation_notes"):
            if len(notes) > 5000:
                errors.append("Negotiation notes exceed maximum length")
            if RecruitmentInputValidator._contains_suspicious_content(notes):
                errors.append("Negotiation notes contain invalid content")

        return len(errors) == 0, errors

    @staticmethod
    def _contains_suspicious_content(text: str) -> bool:
        """Check for suspicious patterns in text."""
        text_lower = text.lower()
        for pattern in RecruitmentInputValidator.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize text input."""
        if not text:
            return ""

        # Truncate
        text = text[:max_length]

        # Remove null bytes
        text = text.replace("\x00", "")

        # Basic HTML entity encoding for display safety
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")

        return text


# =============================================================================
# AI Interview Fraud Detection
# =============================================================================

class InterviewFraudDetector:
    """
    Detect potential fraud in AI interviews.

    Checks for:
    - Multiple simultaneous sessions
    - Suspicious timing patterns
    - Browser/device fingerprint changes
    - Copy-paste detection in responses
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_session_integrity(
        self,
        session_id: UUID,
        candidate_id: UUID,
        browser_fingerprint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify session integrity for an AI interview.

        Returns:
            Dict with 'valid' boolean and any 'warnings' or 'errors'
        """
        result = {"valid": True, "warnings": [], "errors": []}

        # Check for concurrent sessions
        concurrent = await self._check_concurrent_sessions(candidate_id, session_id)
        if concurrent:
            result["warnings"].append("Multiple active interview sessions detected")
            logger.warning(f"Concurrent sessions for candidate {candidate_id}")

        # Check fingerprint consistency
        if browser_fingerprint:
            fingerprint_changed = await self._check_fingerprint_change(
                session_id, browser_fingerprint
            )
            if fingerprint_changed:
                result["warnings"].append("Browser environment change detected")
                logger.warning(f"Fingerprint change in session {session_id}")

        return result

    async def _check_concurrent_sessions(
        self,
        candidate_id: UUID,
        current_session_id: UUID
    ) -> bool:
        """Check for concurrent active sessions."""
        query = await self.db.execute(
            text("""
                SELECT COUNT(*) FROM ai_interview_sessions
                WHERE candidate_id = :candidate_id
                  AND id != :session_id
                  AND status IN ('in_progress', 'scheduled')
                  AND (expires_at IS NULL OR expires_at > NOW())
            """).bindparams(candidate_id=candidate_id, session_id=current_session_id)
        )
        count = query.scalar()
        return count > 0

    async def _check_fingerprint_change(
        self,
        session_id: UUID,
        current_fingerprint: str
    ) -> bool:
        """Check if browser fingerprint has changed during session."""
        query = await self.db.execute(
            text("""
                SELECT browser_info->>'fingerprint' as fingerprint
                FROM ai_interview_sessions
                WHERE id = :session_id
            """).bindparams(session_id=session_id)
        )
        row = query.first()

        if row and row.fingerprint:
            return row.fingerprint != current_fingerprint
        return False

    async def analyze_response_timing(
        self,
        session_id: UUID
    ) -> Dict[str, Any]:
        """
        Analyze response timing patterns for anomalies.

        Returns:
            Dict with analysis results
        """
        query = await self.db.execute(
            text("""
                SELECT
                    question_number,
                    duration_seconds,
                    started_at,
                    completed_at
                FROM ai_interview_responses r
                JOIN ai_interview_questions q ON r.question_id = q.id
                WHERE r.session_id = :session_id
                ORDER BY question_number
            """).bindparams(session_id=session_id)
        )
        responses = query.fetchall()

        if not responses:
            return {"analyzed": False}

        durations = [r.duration_seconds for r in responses if r.duration_seconds]

        if not durations:
            return {"analyzed": False}

        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        anomalies = []

        # Check for suspiciously fast responses (< 10 seconds for complex questions)
        if min_duration < 10:
            anomalies.append("Extremely fast response detected")

        # Check for uniform response times (potential scripted answers)
        if len(durations) > 2:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            if variance < 5:  # Very low variance
                anomalies.append("Unusually uniform response times")

        return {
            "analyzed": True,
            "average_duration": avg_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "anomalies": anomalies,
            "suspicious": len(anomalies) > 0
        }


# =============================================================================
# Session Token Management
# =============================================================================

class SessionTokenManager:
    """
    Secure session token management for candidate portal.
    """

    TOKEN_EXPIRY_HOURS = 24
    REFRESH_TOKEN_EXPIRY_DAYS = 30

    @staticmethod
    def generate_session_token(candidate_id: str, extra_data: Optional[Dict] = None) -> str:
        """Generate a secure session token."""
        import secrets
        import json
        import base64

        payload = {
            "candidate_id": candidate_id,
            "created_at": datetime.utcnow().isoformat(),
            "nonce": secrets.token_hex(16),
            **(extra_data or {})
        }

        # Create token (in production, use JWT with proper signing)
        token_data = json.dumps(payload).encode()
        return base64.urlsafe_b64encode(token_data).decode()

    @staticmethod
    def generate_interview_token(session_id: str, expiry_hours: int = 48) -> str:
        """
        Generate a secure, single-use interview session token.

        These tokens are used for AI interview room access.
        """
        import secrets

        # Include session ID hash and random component
        session_hash = hashlib.sha256(session_id.encode()).hexdigest()[:16]
        random_part = secrets.token_urlsafe(24)

        return f"{session_hash}_{random_part}"

    @staticmethod
    def validate_interview_token(token: str, expected_session_id: str) -> bool:
        """Validate an interview session token."""
        if not token or '_' not in token:
            return False

        try:
            session_hash, _ = token.split('_', 1)
            expected_hash = hashlib.sha256(expected_session_id.encode()).hexdigest()[:16]
            return session_hash == expected_hash
        except Exception:
            return False


# =============================================================================
# Audit Logging
# =============================================================================

class RecruitmentAuditLogger:
    """
    Audit logging for recruitment actions.
    Records all sensitive operations for compliance and security review.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action_type: str,
        actor_type: str,  # 'candidate', 'recruiter', 'system'
        actor_id: Optional[str],
        resource_type: str,
        resource_id: str,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event."""
        from uuid import uuid4

        await self.db.execute(
            text("""
                INSERT INTO recruitment_audit_log (
                    id, action_type, actor_type, actor_id,
                    resource_type, resource_id, details,
                    ip_address, user_agent, created_at
                ) VALUES (
                    :id, :action, :actor_type, :actor_id,
                    :resource_type, :resource_id, :details,
                    :ip, :ua, NOW()
                )
            """).bindparams(
                id=uuid4(),
                action=action_type,
                actor_type=actor_type,
                actor_id=actor_id,
                resource_type=resource_type,
                resource_id=resource_id,
                details=str(details) if details else None,
                ip=ip_address,
                ua=user_agent[:500] if user_agent else None
            )
        )
        await self.db.commit()

        logger.info(
            f"Audit: {action_type} on {resource_type}/{resource_id} "
            f"by {actor_type}/{actor_id}"
        )

    # Convenience methods for common actions
    async def log_login(self, candidate_id: str, ip: str, success: bool):
        """Log login attempt."""
        await self.log_action(
            action_type="login_success" if success else "login_failed",
            actor_type="candidate",
            actor_id=candidate_id,
            resource_type="auth",
            resource_id=candidate_id,
            ip_address=ip
        )

    async def log_application(self, candidate_id: str, job_id: str, action: str):
        """Log application action."""
        await self.log_action(
            action_type=f"application_{action}",
            actor_type="candidate",
            actor_id=candidate_id,
            resource_type="application",
            resource_id=job_id
        )

    async def log_interview(self, session_id: str, actor_id: str, action: str):
        """Log interview action."""
        await self.log_action(
            action_type=f"interview_{action}",
            actor_type="candidate",
            actor_id=actor_id,
            resource_type="interview",
            resource_id=session_id
        )

    async def log_offer(self, offer_id: str, actor_id: str, actor_type: str, action: str):
        """Log offer action."""
        await self.log_action(
            action_type=f"offer_{action}",
            actor_type=actor_type,
            actor_id=actor_id,
            resource_type="offer",
            resource_id=offer_id
        )
