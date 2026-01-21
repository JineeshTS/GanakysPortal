"""
Carbon Emission Service
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import CarbonEmission, EmissionScope
from app.schemas.esg import (
    CarbonEmissionCreate, CarbonEmissionUpdate, CarbonEmissionListResponse,
    EmissionSummaryResponse
)


class EmissionService:
    """Service for managing carbon emissions"""

    async def list_emissions(
        self,
        db: AsyncSession,
        company_id: UUID,
        scope: Optional[EmissionScope] = None,
        category: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        facility_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> CarbonEmissionListResponse:
        """List carbon emissions"""
        conditions = [CarbonEmission.company_id == company_id]

        if scope:
            conditions.append(CarbonEmission.scope == scope)
        if category:
            conditions.append(CarbonEmission.category == category)
        if period_start:
            conditions.append(CarbonEmission.period_start_date >= period_start)
        if period_end:
            conditions.append(CarbonEmission.period_end_date <= period_end)
        if facility_id:
            conditions.append(CarbonEmission.facility_id == facility_id)

        # Get total count
        count_query = select(func.count()).select_from(CarbonEmission).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Get scope totals
        scope1_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(CarbonEmission.company_id == company_id, CarbonEmission.scope == EmissionScope.scope_1)
        )
        scope2_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(CarbonEmission.company_id == company_id, CarbonEmission.scope == EmissionScope.scope_2)
        )
        scope3_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(CarbonEmission.company_id == company_id, CarbonEmission.scope == EmissionScope.scope_3)
        )

        total_scope1 = await db.scalar(scope1_query) or 0
        total_scope2 = await db.scalar(scope2_query) or 0
        total_scope3 = await db.scalar(scope3_query) or 0

        # Get items
        query = (
            select(CarbonEmission)
            .where(and_(*conditions))
            .order_by(CarbonEmission.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        emissions = result.scalars().all()

        return CarbonEmissionListResponse(
            items=list(emissions),
            total=total,
            total_scope1=float(total_scope1),
            total_scope2=float(total_scope2),
            total_scope3=float(total_scope3),
            total_co2e=float(total_scope1 + total_scope2 + total_scope3)
        )

    async def create_emission(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        emission_data: CarbonEmissionCreate
    ) -> CarbonEmission:
        """Create a carbon emission record"""
        emission = CarbonEmission(
            company_id=company_id,
            created_by=user_id,
            **emission_data.model_dump()
        )

        # Calculate CO2e if activity data and emission factor are provided
        if emission.activity_data and emission.emission_factor:
            emission.co2_emissions = emission.activity_data * emission.emission_factor
            emission.total_co2e = emission.co2_emissions

            # Add other GHG contributions if provided
            if emission.ch4_emissions:
                emission.total_co2e += emission.ch4_emissions * Decimal(str(emission.ch4_gwp))
            if emission.n2o_emissions:
                emission.total_co2e += emission.n2o_emissions * Decimal(str(emission.n2o_gwp))
            if emission.hfc_emissions:
                emission.total_co2e += emission.hfc_emissions

        db.add(emission)
        await db.commit()
        await db.refresh(emission)
        return emission

    async def get_emission(
        self,
        db: AsyncSession,
        emission_id: UUID,
        company_id: UUID
    ) -> Optional[CarbonEmission]:
        """Get a specific emission record"""
        query = select(CarbonEmission).where(
            and_(
                CarbonEmission.id == emission_id,
                CarbonEmission.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_emission_summary(
        self,
        db: AsyncSession,
        company_id: UUID,
        period_start: date,
        period_end: date,
        scope: Optional[EmissionScope] = None,
        facility_id: Optional[UUID] = None
    ) -> EmissionSummaryResponse:
        """Get emission summary for a period"""
        conditions = [
            CarbonEmission.company_id == company_id,
            CarbonEmission.period_start_date >= period_start,
            CarbonEmission.period_end_date <= period_end
        ]

        if scope:
            conditions.append(CarbonEmission.scope == scope)
        if facility_id:
            conditions.append(CarbonEmission.facility_id == facility_id)

        # Get totals by scope
        scope1_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(*conditions, CarbonEmission.scope == EmissionScope.scope_1)
        )
        scope2_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(*conditions, CarbonEmission.scope == EmissionScope.scope_2)
        )
        scope3_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(*conditions, CarbonEmission.scope == EmissionScope.scope_3)
        )

        scope1 = await db.scalar(scope1_query) or 0
        scope2 = await db.scalar(scope2_query) or 0
        scope3 = await db.scalar(scope3_query) or 0

        # Get by category
        cat_query = (
            select(CarbonEmission.category, func.sum(CarbonEmission.total_co2e))
            .where(and_(*conditions))
            .group_by(CarbonEmission.category)
        )
        cat_result = await db.execute(cat_query)
        by_category = {row[0]: float(row[1] or 0) for row in cat_result}

        # Get by facility
        fac_query = (
            select(CarbonEmission.facility_name, func.sum(CarbonEmission.total_co2e))
            .where(and_(*conditions, CarbonEmission.facility_name.isnot(None)))
            .group_by(CarbonEmission.facility_name)
        )
        fac_result = await db.execute(fac_query)
        by_facility = {row[0]: float(row[1] or 0) for row in fac_result}

        return EmissionSummaryResponse(
            period_start_date=period_start,
            period_end_date=period_end,
            scope1_total=float(scope1),
            scope2_total=float(scope2),
            scope3_total=float(scope3),
            total_co2e=float(scope1 + scope2 + scope3),
            by_category=by_category,
            by_facility=by_facility
        )


emission_service = EmissionService()
