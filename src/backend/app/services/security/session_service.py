"""
Session Service
Manages user sessions and trusted devices
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.security import (
    SecuritySession, TrustedDevice, DeviceTrustLevel
)
from app.schemas.security import (
    UserSessionResponse, UserSessionListResponse,
    TrustedDeviceResponse, TrustedDeviceListResponse
)


class SessionService:
    """Service for managing user sessions and devices"""

    # ============ Session Methods ============

    async def list_user_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> UserSessionListResponse:
        """List user's active sessions"""
        result = await db.execute(
            select(SecuritySession).where(
                SecuritySession.user_id == user_id,
                SecuritySession.company_id == company_id,
                SecuritySession.is_active == True
            ).order_by(SecuritySession.last_activity_at.desc())
        )
        sessions = result.scalars().all()

        return UserSessionListResponse(
            items=[UserSessionResponse.model_validate(s) for s in sessions],
            total=len(sessions)
        )

    async def list_all_sessions(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> UserSessionListResponse:
        """List all sessions (admin)"""
        query = select(SecuritySession).where(
            SecuritySession.company_id == company_id
        )

        if user_id:
            query = query.where(SecuritySession.user_id == user_id)
        if is_active is not None:
            query = query.where(SecuritySession.is_active == is_active)

        result = await db.execute(
            query.order_by(SecuritySession.last_activity_at.desc())
        )
        sessions = result.scalars().all()

        return UserSessionListResponse(
            items=[UserSessionResponse.model_validate(s) for s in sessions],
            total=len(sessions)
        )

    async def create_session(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        session_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[UUID] = None,
        **kwargs
    ) -> SecuritySession:
        """Create a new session"""
        if not expires_at:
            expires_at = datetime.utcnow() + timedelta(hours=8)

        session = SecuritySession(
            company_id=company_id,
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            **kwargs
        )
        db.add(session)
        await db.flush()
        return session

    async def revoke_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        company_id: UUID,
        revoked_by: UUID,
        reason: Optional[str] = None
    ) -> None:
        """Revoke a specific session"""
        result = await db.execute(
            select(SecuritySession).where(
                SecuritySession.id == session_id,
                SecuritySession.company_id == company_id,
                SecuritySession.is_active == True
            )
        )
        session = result.scalar_one_or_none()

        if session:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            session.revoked_by = revoked_by
            session.revoke_reason = reason
            await db.commit()

    async def revoke_user_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID,
        revoked_by: UUID,
        reason: Optional[str] = None
    ) -> int:
        """Revoke all sessions for a user"""
        result = await db.execute(
            update(SecuritySession)
            .where(
                SecuritySession.user_id == user_id,
                SecuritySession.company_id == company_id,
                SecuritySession.is_active == True
            )
            .values(
                is_active=False,
                revoked_at=datetime.utcnow(),
                revoked_by=revoked_by,
                revoke_reason=reason
            )
        )
        await db.commit()
        return result.rowcount

    async def update_session_activity(
        self,
        db: AsyncSession,
        session_token: str
    ) -> None:
        """Update session last activity time"""
        await db.execute(
            update(SecuritySession)
            .where(SecuritySession.session_token == session_token)
            .values(last_activity_at=datetime.utcnow())
        )
        await db.commit()

    # ============ Device Methods ============

    async def list_user_devices(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> TrustedDeviceListResponse:
        """List user's devices"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.user_id == user_id,
                TrustedDevice.company_id == company_id,
                TrustedDevice.is_active == True
            ).order_by(TrustedDevice.last_seen_at.desc())
        )
        devices = result.scalars().all()

        return TrustedDeviceListResponse(
            items=[TrustedDeviceResponse.model_validate(d) for d in devices],
            total=len(devices)
        )

    async def get_device(
        self,
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID
    ) -> Optional[TrustedDevice]:
        """Get device by ID"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.id == device_id,
                TrustedDevice.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_device(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        device_fingerprint: str,
        ip_address: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs
    ) -> TrustedDevice:
        """Get or create a device record"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.user_id == user_id,
                TrustedDevice.device_fingerprint == device_fingerprint
            )
        )
        device = result.scalar_one_or_none()

        if device:
            # Update last seen
            device.last_seen_at = datetime.utcnow()
            device.last_seen_ip = ip_address
            device.last_seen_location = location
            device.login_count += 1
            await db.flush()
        else:
            # Create new device
            device = TrustedDevice(
                company_id=company_id,
                user_id=user_id,
                device_fingerprint=device_fingerprint,
                first_seen_ip=ip_address,
                first_seen_location=location,
                last_seen_ip=ip_address,
                last_seen_location=location,
                trust_level=DeviceTrustLevel.recognized,
                **kwargs
            )
            db.add(device)
            await db.flush()

        return device

    async def trust_device(
        self,
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID,
        trusted_by: UUID,
        device_name: Optional[str] = None,
        trust_days: int = 30
    ) -> None:
        """Mark device as trusted"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.id == device_id,
                TrustedDevice.company_id == company_id
            )
        )
        device = result.scalar_one_or_none()

        if device:
            device.trust_level = DeviceTrustLevel.trusted
            device.trusted_at = datetime.utcnow()
            device.trusted_by = trusted_by
            device.trusted_until = datetime.utcnow() + timedelta(days=trust_days)
            if device_name:
                device.device_name = device_name
            await db.commit()

    async def block_device(
        self,
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID,
        blocked_by: UUID,
        reason: str
    ) -> None:
        """Block a device"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.id == device_id,
                TrustedDevice.company_id == company_id
            )
        )
        device = result.scalar_one_or_none()

        if device:
            device.trust_level = DeviceTrustLevel.blocked
            device.blocked_at = datetime.utcnow()
            device.blocked_by = blocked_by
            device.block_reason = reason
            await db.commit()

    async def remove_device(
        self,
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID
    ) -> None:
        """Remove device (soft delete)"""
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.id == device_id,
                TrustedDevice.company_id == company_id
            )
        )
        device = result.scalar_one_or_none()

        if device:
            device.is_active = False
            await db.commit()
