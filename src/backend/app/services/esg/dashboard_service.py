"""
ESG Dashboard Service
"""
from datetime import datetime, date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import (
    CarbonEmission, EnergyConsumption, WaterUsage, WasteManagement,
    ESGInitiative, ESGRisk, ESGTarget, ESGCertification, ESGCompanyMetric,
    EmissionScope, ESGInitiativeStatus, ESGRiskLevel, CertificationStatus
)
from app.schemas.esg import ESGDashboardMetrics


class DashboardService:
    """Service for ESG dashboard"""

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> ESGDashboardMetrics:
        """Get comprehensive ESG dashboard metrics"""
        if not period_end:
            period_end = date.today()
        if not period_start:
            period_start = period_end - timedelta(days=365)

        base_emission_condition = and_(
            CarbonEmission.company_id == company_id,
            CarbonEmission.period_start_date >= period_start,
            CarbonEmission.period_end_date <= period_end
        )

        # Emission totals
        scope1_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(base_emission_condition, CarbonEmission.scope == EmissionScope.scope_1)
        )
        scope2_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(base_emission_condition, CarbonEmission.scope == EmissionScope.scope_2)
        )
        scope3_query = select(func.sum(CarbonEmission.total_co2e)).where(
            and_(base_emission_condition, CarbonEmission.scope == EmissionScope.scope_3)
        )

        scope1 = await db.scalar(scope1_query) or 0
        scope2 = await db.scalar(scope2_query) or 0
        scope3 = await db.scalar(scope3_query) or 0

        # Energy totals
        energy_condition = and_(
            EnergyConsumption.company_id == company_id,
            EnergyConsumption.period_start_date >= period_start,
            EnergyConsumption.period_end_date <= period_end
        )
        total_energy_query = select(func.sum(EnergyConsumption.consumption_amount)).where(energy_condition)
        renewable_energy_query = select(func.sum(EnergyConsumption.consumption_amount)).where(
            and_(energy_condition, EnergyConsumption.is_renewable == True)
        )

        total_energy = await db.scalar(total_energy_query) or 0
        renewable_energy = await db.scalar(renewable_energy_query) or 0
        renewable_pct = float(renewable_energy / total_energy * 100) if total_energy > 0 else None

        # Water totals
        water_condition = and_(
            WaterUsage.company_id == company_id,
            WaterUsage.period_start_date >= period_start,
            WaterUsage.period_end_date <= period_end
        )
        water_query = select(func.sum(WaterUsage.withdrawal_amount)).where(water_condition)
        recycled_query = select(func.sum(WaterUsage.recycled_amount)).where(water_condition)

        total_water = await db.scalar(water_query) or 0
        recycled_water = await db.scalar(recycled_query) or 0
        water_recycled_pct = float(recycled_water / total_water * 100) if total_water > 0 else None

        # Waste totals
        waste_condition = and_(
            WasteManagement.company_id == company_id,
            WasteManagement.period_start_date >= period_start,
            WasteManagement.period_end_date <= period_end
        )
        waste_query = select(func.sum(WasteManagement.generated_amount)).where(waste_condition)
        diverted_query = select(
            func.sum(WasteManagement.recycled_amount) + func.sum(WasteManagement.composted_amount)
        ).where(waste_condition)

        total_waste = await db.scalar(waste_query) or 0
        diverted_waste = await db.scalar(diverted_query) or 0
        diversion_rate = float(diverted_waste / total_waste * 100) if total_waste > 0 else None

        # Initiatives
        init_base = ESGInitiative.company_id == company_id
        total_init_query = select(func.count()).select_from(ESGInitiative).where(init_base)
        in_progress_query = select(func.count()).select_from(ESGInitiative).where(
            and_(init_base, ESGInitiative.status == ESGInitiativeStatus.in_progress)
        )
        completed_query = select(func.count()).select_from(ESGInitiative).where(
            and_(init_base, ESGInitiative.status == ESGInitiativeStatus.completed)
        )
        budget_query = select(func.sum(ESGInitiative.budget_amount)).where(init_base)
        spend_query = select(func.sum(ESGInitiative.actual_spend)).where(init_base)

        total_initiatives = await db.scalar(total_init_query) or 0
        initiatives_in_progress = await db.scalar(in_progress_query) or 0
        initiatives_completed = await db.scalar(completed_query) or 0
        total_budget = await db.scalar(budget_query) or 0
        total_spend = await db.scalar(spend_query) or 0

        # Risks
        risk_base = and_(ESGRisk.company_id == company_id, ESGRisk.is_active == True)
        total_risks_query = select(func.count()).select_from(ESGRisk).where(risk_base)
        critical_risks_query = select(func.count()).select_from(ESGRisk).where(
            and_(risk_base, ESGRisk.risk_level == ESGRiskLevel.critical)
        )
        high_risks_query = select(func.count()).select_from(ESGRisk).where(
            and_(risk_base, ESGRisk.risk_level == ESGRiskLevel.high)
        )

        total_risks = await db.scalar(total_risks_query) or 0
        critical_risks = await db.scalar(critical_risks_query) or 0
        high_risks = await db.scalar(high_risks_query) or 0

        # Targets
        target_base = and_(ESGTarget.company_id == company_id, ESGTarget.is_active == True)
        total_targets_query = select(func.count()).select_from(ESGTarget).where(target_base)
        on_track_query = select(func.count()).select_from(ESGTarget).where(
            and_(target_base, ESGTarget.on_track == True)
        )
        at_risk_query = select(func.count()).select_from(ESGTarget).where(
            and_(target_base, ESGTarget.on_track == False)
        )

        total_targets = await db.scalar(total_targets_query) or 0
        targets_on_track = await db.scalar(on_track_query) or 0
        targets_at_risk = await db.scalar(at_risk_query) or 0

        # Certifications
        cert_base = ESGCertification.company_id == company_id
        active_certs_query = select(func.count()).select_from(ESGCertification).where(
            and_(cert_base, ESGCertification.status == CertificationStatus.achieved)
        )
        expiring_query = select(func.count()).select_from(ESGCertification).where(
            and_(
                cert_base,
                ESGCertification.status == CertificationStatus.achieved,
                ESGCertification.expiry_date <= date.today() + timedelta(days=90)
            )
        )

        active_certifications = await db.scalar(active_certs_query) or 0
        certifications_expiring = await db.scalar(expiring_query) or 0

        # Recent metrics
        recent_metrics_query = (
            select(ESGCompanyMetric)
            .where(ESGCompanyMetric.company_id == company_id)
            .order_by(ESGCompanyMetric.created_at.desc())
            .limit(5)
        )
        recent_metrics_result = await db.execute(recent_metrics_query)
        recent_metrics = list(recent_metrics_result.scalars().all())

        # Recent initiatives
        recent_init_query = (
            select(ESGInitiative)
            .where(ESGInitiative.company_id == company_id)
            .order_by(ESGInitiative.created_at.desc())
            .limit(5)
        )
        recent_init_result = await db.execute(recent_init_query)
        recent_initiatives = list(recent_init_result.scalars().all())

        return ESGDashboardMetrics(
            total_scope1_emissions=float(scope1),
            total_scope2_emissions=float(scope2),
            total_scope3_emissions=float(scope3),
            total_emissions=float(scope1 + scope2 + scope3),
            total_energy_consumption=float(total_energy),
            renewable_energy_pct=renewable_pct,
            total_water_withdrawal=float(total_water),
            water_recycled_pct=water_recycled_pct,
            total_waste_generated=float(total_waste),
            waste_diversion_rate=diversion_rate,
            total_initiatives=total_initiatives,
            initiatives_in_progress=initiatives_in_progress,
            initiatives_completed=initiatives_completed,
            total_budget=float(total_budget),
            total_spend=float(total_spend),
            total_risks=total_risks,
            critical_risks=critical_risks,
            high_risks=high_risks,
            total_targets=total_targets,
            targets_on_track=targets_on_track,
            targets_at_risk=targets_at_risk,
            active_certifications=active_certifications,
            certifications_expiring_soon=certifications_expiring,
            recent_metrics=recent_metrics,
            recent_initiatives=recent_initiatives
        )


dashboard_service = DashboardService()
