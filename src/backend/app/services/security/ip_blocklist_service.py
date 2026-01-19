"""
IP Blocklist Service
Manages IP blocking
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.security import IPBlocklist
from app.schemas.security import IPBlockCreate, IPBlockResponse, IPBlockListResponse
from app.core.datetime_utils import utc_now


class IPBlocklistService:
    """Service for managing IP blocklist"""

    async def list_blocked_ips(
        self,
        db: AsyncSession,
        company_id: UUID,
        is_active: bool = True
    ) -> IPBlockListResponse:
        """List blocked IPs for company"""
        query = select(IPBlocklist).where(
            or_(
                IPBlocklist.company_id == company_id,
                IPBlocklist.company_id.is_(None)  # Global blocks
            )
        )

        if is_active is not None:
            query = query.where(IPBlocklist.is_active == is_active)

        result = await db.execute(
            query.order_by(IPBlocklist.blocked_at.desc())
        )
        blocks = result.scalars().all()

        return IPBlockListResponse(
            items=[IPBlockResponse.model_validate(b) for b in blocks],
            total=len(blocks)
        )

    async def block_ip(
        self,
        db: AsyncSession,
        company_id: UUID,
        data: IPBlockCreate,
        blocked_by: UUID
    ) -> IPBlocklist:
        """Block an IP address"""
        # Check if already blocked
        result = await db.execute(
            select(IPBlocklist).where(
                IPBlocklist.ip_address == data.ip_address,
                or_(
                    IPBlocklist.company_id == company_id,
                    IPBlocklist.company_id.is_(None)
                ),
                IPBlocklist.is_active == True
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing block
            existing.block_count += 1
            existing.last_blocked_at = utc_now()
            await db.commit()
            await db.refresh(existing)
            return existing

        # Create new block
        block = IPBlocklist(
            company_id=company_id,
            ip_address=data.ip_address,
            reason=data.reason,
            expires_at=data.expires_at,
            incident_id=data.incident_id,
            blocked_by=blocked_by,
            block_type="manual"
        )

        db.add(block)
        await db.commit()
        await db.refresh(block)

        return block

    async def unblock_ip(
        self,
        db: AsyncSession,
        block_id: UUID,
        company_id: UUID
    ) -> None:
        """Unblock an IP"""
        result = await db.execute(
            select(IPBlocklist).where(
                IPBlocklist.id == block_id,
                IPBlocklist.company_id == company_id
            )
        )
        block = result.scalar_one_or_none()

        if block:
            block.is_active = False
            await db.commit()

    async def is_ip_blocked(
        self,
        db: AsyncSession,
        ip_address: str,
        company_id: Optional[UUID] = None
    ) -> bool:
        """Check if an IP is blocked"""
        now = utc_now()

        query = select(IPBlocklist).where(
            IPBlocklist.ip_address == ip_address,
            IPBlocklist.is_active == True,
            or_(
                IPBlocklist.expires_at.is_(None),
                IPBlocklist.expires_at > now
            )
        )

        if company_id:
            query = query.where(
                or_(
                    IPBlocklist.company_id == company_id,
                    IPBlocklist.company_id.is_(None)  # Include global blocks
                )
            )

        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def auto_block_ip(
        self,
        db: AsyncSession,
        ip_address: str,
        reason: str,
        company_id: Optional[UUID] = None,
        incident_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None
    ) -> IPBlocklist:
        """Automatically block an IP (e.g., after failed logins)"""
        # Check if already blocked
        query = select(IPBlocklist).where(
            IPBlocklist.ip_address == ip_address,
            IPBlocklist.is_active == True
        )
        if company_id:
            query = query.where(
                or_(
                    IPBlocklist.company_id == company_id,
                    IPBlocklist.company_id.is_(None)
                )
            )

        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            existing.block_count += 1
            existing.last_blocked_at = utc_now()
            await db.commit()
            return existing

        block = IPBlocklist(
            company_id=company_id,
            ip_address=ip_address,
            reason=reason,
            block_type="automatic",
            incident_id=incident_id,
            expires_at=expires_at
        )

        db.add(block)
        await db.commit()
        await db.refresh(block)

        return block

    async def record_blocked_attempt(
        self,
        db: AsyncSession,
        ip_address: str
    ) -> None:
        """Record a blocked access attempt"""
        result = await db.execute(
            select(IPBlocklist).where(
                IPBlocklist.ip_address == ip_address,
                IPBlocklist.is_active == True
            )
        )
        block = result.scalar_one_or_none()

        if block:
            block.block_count += 1
            block.last_blocked_at = utc_now()
            await db.commit()
