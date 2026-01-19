"""
Anomaly Rule Service
Handles CRUD operations for anomaly detection rules
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_detection import AnomalyRule, AnomalyCategory
from app.schemas.anomaly_detection import AnomalyRuleCreate, AnomalyRuleUpdate
from app.core.datetime_utils import utc_now


class RuleService:
    """Service for managing anomaly detection rules"""

    async def list_rules(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[AnomalyCategory] = None,
        data_source: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[AnomalyRule], int]:
        """List rules with filters"""
        conditions = [AnomalyRule.company_id == company_id]

        if category:
            conditions.append(AnomalyRule.category == category)
        if data_source:
            conditions.append(AnomalyRule.data_source == data_source)
        if is_active is not None:
            conditions.append(AnomalyRule.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(AnomalyRule).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Get items
        query = (
            select(AnomalyRule)
            .where(and_(*conditions))
            .order_by(AnomalyRule.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        rules = result.scalars().all()

        return list(rules), total

    async def create_rule(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        rule_data: AnomalyRuleCreate
    ) -> AnomalyRule:
        """Create a new anomaly rule"""
        rule = AnomalyRule(
            company_id=company_id,
            created_by=user_id,
            name=rule_data.name,
            description=rule_data.description,
            code=rule_data.code,
            category=rule_data.category,
            data_source=rule_data.data_source,
            entity_type=rule_data.entity_type,
            conditions=rule_data.conditions,
            aggregation_period=rule_data.aggregation_period,
            aggregation_function=rule_data.aggregation_function,
            group_by_fields=rule_data.group_by_fields,
            severity=rule_data.severity,
            confidence_threshold=rule_data.confidence_threshold,
            baseline_period_days=rule_data.baseline_period_days,
            min_data_points=rule_data.min_data_points,
            alert_enabled=rule_data.alert_enabled,
            alert_recipients=rule_data.alert_recipients,
            cooldown_minutes=rule_data.cooldown_minutes,
            is_active=True,
            is_system_rule=False
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    async def get_rule(
        self,
        db: AsyncSession,
        rule_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyRule]:
        """Get a specific rule"""
        query = select(AnomalyRule).where(
            and_(
                AnomalyRule.id == rule_id,
                AnomalyRule.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_rule(
        self,
        db: AsyncSession,
        rule_id: UUID,
        company_id: UUID,
        rule_data: AnomalyRuleUpdate
    ) -> Optional[AnomalyRule]:
        """Update a rule"""
        rule = await self.get_rule(db, rule_id, company_id)
        if not rule:
            return None

        # Don't allow updating system rules
        if rule.is_system_rule:
            return None

        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        rule.updated_at = utc_now()
        await db.commit()
        await db.refresh(rule)
        return rule

    async def delete_rule(
        self,
        db: AsyncSession,
        rule_id: UUID,
        company_id: UUID
    ) -> bool:
        """Delete a rule"""
        rule = await self.get_rule(db, rule_id, company_id)
        if not rule or rule.is_system_rule:
            return False

        await db.delete(rule)
        await db.commit()
        return True

    async def toggle_rule(
        self,
        db: AsyncSession,
        rule_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyRule]:
        """Toggle rule active status"""
        rule = await self.get_rule(db, rule_id, company_id)
        if not rule:
            return None

        rule.is_active = not rule.is_active
        rule.updated_at = utc_now()
        await db.commit()
        await db.refresh(rule)
        return rule

    async def get_active_rules(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[AnomalyCategory] = None,
        data_source: Optional[str] = None
    ) -> List[AnomalyRule]:
        """Get active rules for detection"""
        conditions = [
            AnomalyRule.company_id == company_id,
            AnomalyRule.is_active == True
        ]

        if category:
            conditions.append(AnomalyRule.category == category)
        if data_source:
            conditions.append(AnomalyRule.data_source == data_source)

        query = select(AnomalyRule).where(and_(*conditions))
        result = await db.execute(query)
        return list(result.scalars().all())


rule_service = RuleService()
