"""
ESG Risk Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGRisk, ESGCategory, ESGRiskLevel
from app.schemas.esg import ESGRiskCreate, ESGRiskUpdate, ESGRiskListResponse


class RiskService:
    """Service for managing ESG risks"""

    async def list_risks(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[ESGCategory] = None,
        risk_level: Optional[ESGRiskLevel] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50
    ) -> ESGRiskListResponse:
        """List ESG risks"""
        conditions = [ESGRisk.company_id == company_id]

        if category:
            conditions.append(ESGRisk.category == category)
        if risk_level:
            conditions.append(ESGRisk.risk_level == risk_level)
        if is_active is not None:
            conditions.append(ESGRisk.is_active == is_active)

        count_query = select(func.count()).select_from(ESGRisk).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        query = (
            select(ESGRisk)
            .where(and_(*conditions))
            .order_by(ESGRisk.risk_score.desc().nulls_last())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        risks = result.scalars().all()

        return ESGRiskListResponse(items=list(risks), total=total)

    async def create_risk(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        risk_data: ESGRiskCreate
    ) -> ESGRisk:
        """Create an ESG risk"""
        risk = ESGRisk(
            company_id=company_id,
            created_by=user_id,
            is_active=True,
            **risk_data.model_dump()
        )

        # Calculate risk score
        if risk.likelihood and risk.impact:
            risk.risk_score = risk.likelihood * risk.impact

        db.add(risk)
        await db.commit()
        await db.refresh(risk)
        return risk

    async def get_risk(
        self,
        db: AsyncSession,
        risk_id: UUID,
        company_id: UUID
    ) -> Optional[ESGRisk]:
        """Get a specific risk"""
        query = select(ESGRisk).where(
            and_(ESGRisk.id == risk_id, ESGRisk.company_id == company_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_risk(
        self,
        db: AsyncSession,
        risk_id: UUID,
        company_id: UUID,
        risk_data: ESGRiskUpdate
    ) -> Optional[ESGRisk]:
        """Update a risk"""
        risk = await self.get_risk(db, risk_id, company_id)
        if not risk:
            return None

        update_data = risk_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(risk, field, value)

        # Recalculate risk score
        if risk.likelihood and risk.impact:
            risk.risk_score = risk.likelihood * risk.impact

        risk.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(risk)
        return risk


risk_service = RiskService()
