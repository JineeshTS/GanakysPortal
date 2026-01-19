"""
Compliance Master Service
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance import ComplianceMaster, ComplianceTask, ComplianceCategory, ComplianceStatus, ComplianceFrequency
from app.schemas.compliance import ComplianceMasterCreate, ComplianceMasterUpdate
from app.core.datetime_utils import utc_now


class ComplianceService:
    async def create(self, db: AsyncSession, obj_in: ComplianceMasterCreate, company_id: UUID, user_id: UUID) -> ComplianceMaster:
        compliance_code = await self._generate_code(db, company_id)
        db_obj = ComplianceMaster(
            id=uuid4(), company_id=company_id, compliance_code=compliance_code,
            name=obj_in.name, description=obj_in.description, category=obj_in.category,
            act_name=obj_in.act_name, section_rule=obj_in.section_rule, regulator=obj_in.regulator,
            jurisdiction=obj_in.jurisdiction, applicable_to=obj_in.applicable_to,
            industry_types=obj_in.industry_types, threshold_conditions=obj_in.threshold_conditions,
            frequency=obj_in.frequency, due_day=obj_in.due_day, due_month=obj_in.due_month,
            grace_days=obj_in.grace_days or 0, advance_reminder_days=obj_in.advance_reminder_days or 7,
            risk_level=obj_in.risk_level, penalty_type=obj_in.penalty_type, penalty_amount=obj_in.penalty_amount,
            penalty_description=obj_in.penalty_description, required_documents=obj_in.required_documents,
            forms_required=obj_in.forms_required, submission_mode=obj_in.submission_mode,
            submission_portal=obj_in.submission_portal, default_owner_role=obj_in.default_owner_role,
            departments=obj_in.departments, compliance_steps=obj_in.compliance_steps,
            reference_links=obj_in.reference_links, is_active=True, created_by=user_id, created_at=utc_now(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[ComplianceMaster]:
        result = await db.execute(select(ComplianceMaster).where(and_(ComplianceMaster.id == id, ComplianceMaster.company_id == company_id)))
        return result.scalar_one_or_none()

    async def get_list(self, db: AsyncSession, company_id: UUID, page: int = 1, size: int = 20,
                       search: Optional[str] = None, category: Optional[ComplianceCategory] = None,
                       is_active: Optional[bool] = None) -> Tuple[List[ComplianceMaster], int]:
        query = select(ComplianceMaster).where(ComplianceMaster.company_id == company_id)
        count_query = select(func.count(ComplianceMaster.id)).where(ComplianceMaster.company_id == company_id)
        if search:
            sf = or_(ComplianceMaster.name.ilike(f"%{search}%"), ComplianceMaster.compliance_code.ilike(f"%{search}%"))
            query = query.where(sf)
            count_query = count_query.where(sf)
        if category:
            query = query.where(ComplianceMaster.category == category)
            count_query = count_query.where(ComplianceMaster.category == category)
        if is_active is not None:
            query = query.where(ComplianceMaster.is_active == is_active)
            count_query = count_query.where(ComplianceMaster.is_active == is_active)
        total = (await db.execute(count_query)).scalar()
        offset = (page - 1) * size
        query = query.order_by(ComplianceMaster.name).offset(offset).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, db: AsyncSession, db_obj: ComplianceMaster, obj_in: ComplianceMasterUpdate) -> ComplianceMaster:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def generate_tasks(self, db: AsyncSession, compliance: ComplianceMaster, financial_year: str, user_id: UUID) -> List[ComplianceTask]:
        tasks = []
        fy_parts = financial_year.split("-")
        start_year = int(fy_parts[0])
        start_date = date(start_year, 4, 1)
        end_date = date(start_year + 1, 3, 31)
        
        current = start_date
        task_count = 0
        while current <= end_date:
            due = self._calculate_due_date(compliance, current)
            if due and start_date <= due <= end_date:
                task_count += 1
                task = ComplianceTask(
                    id=uuid4(), company_id=compliance.company_id, compliance_id=compliance.id,
                    task_code=f"{compliance.compliance_code}-{financial_year}-{task_count:03d}",
                    period=self._get_period_name(compliance.frequency, current),
                    financial_year=financial_year, status=ComplianceStatus.pending,
                    due_date=due, created_by=user_id, created_at=utc_now(),
                )
                db.add(task)
                tasks.append(task)
            current = self._get_next_period(compliance.frequency, current)
            if current is None:
                break
        await db.commit()
        return tasks

    def _calculate_due_date(self, compliance: ComplianceMaster, period_date: date) -> Optional[date]:
        if compliance.frequency == ComplianceFrequency.monthly:
            day = compliance.due_day or 15
            return date(period_date.year, period_date.month, min(day, 28))
        elif compliance.frequency == ComplianceFrequency.quarterly:
            quarter_end_months = [6, 9, 12, 3]
            for m in quarter_end_months:
                if period_date.month <= m or (m == 3 and period_date.month > 12):
                    year = period_date.year if m != 3 else period_date.year + 1
                    day = compliance.due_day or 15
                    return date(year, m, min(day, 28))
        elif compliance.frequency == ComplianceFrequency.annual:
            month = compliance.due_month or 7
            day = compliance.due_day or 31
            return date(period_date.year if period_date.month < month else period_date.year + 1, month, min(day, 28))
        return None

    def _get_period_name(self, frequency: ComplianceFrequency, d: date) -> str:
        if frequency == ComplianceFrequency.monthly:
            return d.strftime("%b-%Y")
        elif frequency == ComplianceFrequency.quarterly:
            q = (d.month - 1) // 3 + 1
            return f"Q{q}-{d.year}"
        elif frequency == ComplianceFrequency.annual:
            return f"FY{d.year}-{str(d.year + 1)[2:]}"
        return d.strftime("%Y-%m-%d")

    def _get_next_period(self, frequency: ComplianceFrequency, current: date) -> Optional[date]:
        if frequency == ComplianceFrequency.monthly:
            return current + relativedelta(months=1)
        elif frequency == ComplianceFrequency.quarterly:
            return current + relativedelta(months=3)
        elif frequency == ComplianceFrequency.annual:
            return current + relativedelta(years=1)
        elif frequency == ComplianceFrequency.one_time:
            return None
        return current + relativedelta(months=1)

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        result = await db.execute(select(func.count(ComplianceMaster.id)).where(ComplianceMaster.company_id == company_id))
        count = result.scalar() or 0
        return f"COMP-{count + 1:04d}"


compliance_service = ComplianceService()
