"""
Legal Party Service
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalParty
from app.schemas.legal import LegalPartyCreate, LegalPartyUpdate
from app.core.datetime_utils import utc_now


class PartyService:
    """Service for legal party operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalPartyCreate,
        company_id: UUID,
    ) -> LegalParty:
        """Add a party to a case"""
        db_obj = LegalParty(
            id=uuid4(),
            company_id=company_id,
            case_id=obj_in.case_id,
            party_name=obj_in.party_name,
            party_type=obj_in.party_type,
            role=obj_in.role,
            contact_person=obj_in.contact_person,
            email=obj_in.email,
            phone=obj_in.phone,
            address=obj_in.address,
            counsel_name=obj_in.counsel_name,
            counsel_firm=obj_in.counsel_firm,
            counsel_contact=obj_in.counsel_contact,
            pan_number=obj_in.pan_number,
            cin_number=obj_in.cin_number,
            notes=obj_in.notes,
            created_at=utc_now(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[LegalParty]:
        """Get party by ID"""
        result = await db.execute(
            select(LegalParty).where(
                and_(
                    LegalParty.id == id,
                    LegalParty.company_id == company_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_case(
        self,
        db: AsyncSession,
        case_id: UUID,
        company_id: UUID,
    ) -> List[LegalParty]:
        """Get parties for a case"""
        result = await db.execute(
            select(LegalParty).where(
                and_(
                    LegalParty.case_id == case_id,
                    LegalParty.company_id == company_id,
                )
            ).order_by(LegalParty.created_at)
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalParty,
        obj_in: LegalPartyUpdate,
    ) -> LegalParty:
        """Update party"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        db_obj: LegalParty,
    ) -> None:
        """Delete party"""
        await db.delete(db_obj)
        await db.commit()


party_service = PartyService()
