"""Compliance Risk Assessment Service"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import ComplianceRiskAssessment, RiskLevel
from app.schemas.compliance import RiskAssessmentCreate, RiskAssessmentUpdate

class RiskService:
    async def create(self, db: AsyncSession, obj_in: RiskAssessmentCreate, company_id: UUID, user_id: UUID) -> ComplianceRiskAssessment:
        assessment_code = f"RISK-{datetime.now().year}-{uuid4().hex[:6].upper()}"
        risk_score = obj_in.likelihood_score * obj_in.impact_score
        risk_level = self._calculate_risk_level(risk_score)
        db_obj = ComplianceRiskAssessment(
            id=uuid4(), company_id=company_id, compliance_id=obj_in.compliance_id,
            assessment_code=assessment_code, assessment_date=obj_in.assessment_date,
            assessment_period=obj_in.assessment_period, likelihood_score=obj_in.likelihood_score,
            impact_score=obj_in.impact_score, risk_score=risk_score, risk_level=risk_level,
            risk_description=obj_in.risk_description, potential_consequences=obj_in.potential_consequences,
            existing_controls=obj_in.existing_controls, control_effectiveness=obj_in.control_effectiveness,
            mitigation_plan=obj_in.mitigation_plan, mitigation_owner=obj_in.mitigation_owner,
            target_date=obj_in.target_date, status="open", assessed_by=user_id, created_at=datetime.utcnow(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[ComplianceRiskAssessment]:
        result = await db.execute(select(ComplianceRiskAssessment).where(and_(
            ComplianceRiskAssessment.id == id, ComplianceRiskAssessment.company_id == company_id)))
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, db_obj: ComplianceRiskAssessment, obj_in: RiskAssessmentUpdate) -> ComplianceRiskAssessment:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        if obj_in.likelihood_score or obj_in.impact_score:
            db_obj.risk_score = db_obj.likelihood_score * db_obj.impact_score
            db_obj.risk_level = self._calculate_risk_level(db_obj.risk_score)
        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def _calculate_risk_level(self, score: int) -> RiskLevel:
        if score >= 20: return RiskLevel.critical
        elif score >= 12: return RiskLevel.high
        elif score >= 6: return RiskLevel.medium
        return RiskLevel.low

risk_service = RiskService()
