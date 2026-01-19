"""
Security Policy Service
Manages company security policies
"""
import re
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.datetime_utils import utc_now
from app.models.security import SecurityPolicy
from app.schemas.security import (
    SecurityPolicyResponse, SecurityPolicyUpdate, PasswordValidationResult
)


class SecurityPolicyService:
    """Service for managing security policies"""

    async def get_or_create_policy(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> SecurityPolicy:
        """Get or create security policy for company"""
        result = await db.execute(
            select(SecurityPolicy).where(
                SecurityPolicy.company_id == company_id
            )
        )
        policy = result.scalar_one_or_none()

        if not policy:
            policy = SecurityPolicy(company_id=company_id)
            db.add(policy)
            await db.commit()
            await db.refresh(policy)

        return policy

    async def update_policy(
        self,
        db: AsyncSession,
        company_id: UUID,
        data: SecurityPolicyUpdate,
        updated_by: UUID
    ) -> SecurityPolicy:
        """Update security policy"""
        policy = await self.get_or_create_policy(db, company_id)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)

        policy.updated_at = utc_now()
        policy.updated_by = updated_by

        await db.commit()
        await db.refresh(policy)

        return policy

    async def validate_password(
        self,
        db: AsyncSession,
        company_id: UUID,
        password: str
    ) -> PasswordValidationResult:
        """Validate password against security policy"""
        policy = await self.get_or_create_policy(db, company_id)

        errors = []
        suggestions = []
        score = 0

        # Check length
        if len(password) < policy.password_min_length:
            errors.append(f"Password must be at least {policy.password_min_length} characters")
        else:
            score += 20

        # Check uppercase
        if policy.password_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        elif re.search(r'[A-Z]', password):
            score += 15

        # Check lowercase
        if policy.password_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        elif re.search(r'[a-z]', password):
            score += 15

        # Check numbers
        if policy.password_require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        elif re.search(r'\d', password):
            score += 15

        # Check special characters
        if policy.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        elif re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15

        # Additional scoring
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10

        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'abc123']
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                score -= 20
                suggestions.append("Avoid common patterns like 'password' or '123456'")
                break

        # Suggestions
        if len(password) < 12:
            suggestions.append("Consider using a longer password for better security")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("Adding special characters increases security")

        return PasswordValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            strength_score=max(0, min(100, score)),
            suggestions=suggestions
        )
