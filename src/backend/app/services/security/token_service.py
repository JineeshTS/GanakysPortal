"""
Access Token Service
Manages API access tokens
"""
import secrets
import hashlib
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.datetime_utils import utc_now
from app.models.security import AccessToken, TokenType
from app.schemas.security import (
    AccessTokenCreate, AccessTokenResponse, AccessTokenCreatedResponse,
    AccessTokenListResponse
)


class AccessTokenService:
    """Service for managing API access tokens"""

    def _generate_token(self) -> tuple[str, str, str]:
        """Generate a new token, returning (full_token, prefix, hash)"""
        token = secrets.token_urlsafe(32)
        prefix = token[:8]
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, prefix, token_hash

    async def list_user_tokens(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> AccessTokenListResponse:
        """List user's access tokens"""
        result = await db.execute(
            select(AccessToken).where(
                AccessToken.user_id == user_id,
                AccessToken.company_id == company_id,
                AccessToken.is_active == True
            ).order_by(AccessToken.created_at.desc())
        )
        tokens = result.scalars().all()

        return AccessTokenListResponse(
            items=[AccessTokenResponse.model_validate(t) for t in tokens],
            total=len(tokens)
        )

    async def list_company_tokens(
        self,
        db: AsyncSession,
        company_id: UUID,
        token_type: Optional[TokenType] = None,
        is_active: bool = True
    ) -> AccessTokenListResponse:
        """List all company tokens"""
        query = select(AccessToken).where(
            AccessToken.company_id == company_id
        )

        if token_type:
            query = query.where(AccessToken.token_type == token_type)
        if is_active is not None:
            query = query.where(AccessToken.is_active == is_active)

        result = await db.execute(
            query.order_by(AccessToken.created_at.desc())
        )
        tokens = result.scalars().all()

        return AccessTokenListResponse(
            items=[AccessTokenResponse.model_validate(t) for t in tokens],
            total=len(tokens)
        )

    async def create_token(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID],
        data: AccessTokenCreate
    ) -> AccessTokenCreatedResponse:
        """Create a new access token"""
        token, prefix, token_hash = self._generate_token()

        access_token = AccessToken(
            company_id=company_id,
            user_id=user_id,
            name=data.name,
            description=data.description,
            token_type=data.token_type,
            token_hash=token_hash,
            token_prefix=prefix,
            scopes=data.scopes,
            permissions=data.permissions,
            rate_limit_per_minute=data.rate_limit_per_minute,
            rate_limit_per_hour=data.rate_limit_per_hour,
            ip_whitelist=data.ip_whitelist,
            ip_whitelist_enabled=data.ip_whitelist_enabled,
            expires_at=data.expires_at,
            created_by=user_id
        )

        db.add(access_token)
        await db.commit()
        await db.refresh(access_token)

        # Return response with full token (only shown once)
        response_data = AccessTokenResponse.model_validate(access_token).model_dump()
        response_data['token'] = token

        return AccessTokenCreatedResponse(**response_data)

    async def get_token(
        self,
        db: AsyncSession,
        token_id: UUID,
        company_id: UUID
    ) -> Optional[AccessToken]:
        """Get token by ID"""
        result = await db.execute(
            select(AccessToken).where(
                AccessToken.id == token_id,
                AccessToken.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def verify_token(
        self,
        db: AsyncSession,
        token: str
    ) -> Optional[AccessToken]:
        """Verify a token and return the access token record"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        result = await db.execute(
            select(AccessToken).where(
                AccessToken.token_hash == token_hash,
                AccessToken.is_active == True
            )
        )
        access_token = result.scalar_one_or_none()

        if not access_token:
            return None

        # Check expiry
        if access_token.expires_at and access_token.expires_at < utc_now():
            return None

        # Update usage
        access_token.last_used_at = utc_now()
        access_token.usage_count += 1
        await db.commit()

        return access_token

    async def revoke_token(
        self,
        db: AsyncSession,
        token_id: UUID,
        company_id: UUID,
        revoked_by: UUID
    ) -> None:
        """Revoke an access token"""
        result = await db.execute(
            select(AccessToken).where(
                AccessToken.id == token_id,
                AccessToken.company_id == company_id,
                AccessToken.is_active == True
            )
        )
        token = result.scalar_one_or_none()

        if token:
            token.is_active = False
            token.revoked_at = utc_now()
            token.revoked_by = revoked_by
            await db.commit()

    async def update_token_usage(
        self,
        db: AsyncSession,
        token_hash: str,
        ip_address: Optional[str] = None
    ) -> None:
        """Update token usage statistics"""
        result = await db.execute(
            select(AccessToken).where(
                AccessToken.token_hash == token_hash
            )
        )
        token = result.scalar_one_or_none()

        if token:
            token.last_used_at = utc_now()
            token.last_used_ip = ip_address
            token.usage_count += 1
            await db.commit()
