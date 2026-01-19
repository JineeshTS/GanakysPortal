"""
Policy Service - Expense Management Module (MOD-21)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.expense import ExpensePolicy, PerDiemRate, MileageRate
from app.schemas.expense import (
    ExpensePolicyCreate, ExpensePolicyUpdate,
    PerDiemRateCreate, PerDiemRateUpdate,
    MileageRateCreate, MileageRateUpdate
)


class PolicyService:
    """Service for expense policy management."""

    # Policy Methods
    @staticmethod
    async def create_policy(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: ExpensePolicyCreate
    ) -> ExpensePolicy:
        """Create an expense policy."""
        policy = ExpensePolicy(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def get_policy(
        db: AsyncSession,
        policy_id: UUID,
        company_id: UUID
    ) -> Optional[ExpensePolicy]:
        """Get expense policy by ID."""
        result = await db.execute(
            select(ExpensePolicy).where(
                and_(
                    ExpensePolicy.id == policy_id,
                    ExpensePolicy.company_id == company_id,
                    ExpensePolicy.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_policies(
        db: AsyncSession,
        company_id: UUID,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExpensePolicy], int]:
        """List expense policies."""
        query = select(ExpensePolicy).where(
            and_(
                ExpensePolicy.company_id == company_id,
                ExpensePolicy.deleted_at.is_(None)
            )
        )

        if is_active is not None:
            query = query.where(ExpensePolicy.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExpensePolicy.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_policy(
        db: AsyncSession,
        policy: ExpensePolicy,
        data: ExpensePolicyUpdate
    ) -> ExpensePolicy:
        """Update expense policy."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        policy.updated_at = utc_now()
        await db.commit()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def get_applicable_policy(
        db: AsyncSession,
        company_id: UUID,
        employee_department_id: Optional[UUID] = None,
        employee_designation_id: Optional[UUID] = None,
        employee_grade: Optional[str] = None
    ) -> Optional[ExpensePolicy]:
        """Get applicable expense policy for an employee."""
        today = date.today()

        # First try to find a specific policy
        query = select(ExpensePolicy).where(
            and_(
                ExpensePolicy.company_id == company_id,
                ExpensePolicy.is_active == True,
                ExpensePolicy.effective_from <= today,
                (ExpensePolicy.effective_to.is_(None)) | (ExpensePolicy.effective_to >= today),
                ExpensePolicy.deleted_at.is_(None)
            )
        )

        result = await db.execute(query)
        policies = result.scalars().all()

        # Find best matching policy
        for policy in policies:
            if policy.applies_to_all:
                return policy

            if employee_department_id and policy.department_ids:
                if str(employee_department_id) in policy.department_ids:
                    return policy

            if employee_designation_id and policy.designation_ids:
                if str(employee_designation_id) in policy.designation_ids:
                    return policy

            if employee_grade and policy.grade_levels:
                if employee_grade in policy.grade_levels:
                    return policy

        # Return default policy if exists
        for policy in policies:
            if policy.applies_to_all:
                return policy

        return None

    @staticmethod
    async def delete_policy(
        db: AsyncSession,
        policy: ExpensePolicy
    ) -> None:
        """Soft delete policy."""
        policy.deleted_at = utc_now()
        await db.commit()

    # Per Diem Rate Methods
    @staticmethod
    async def create_per_diem_rate(
        db: AsyncSession,
        company_id: UUID,
        data: PerDiemRateCreate
    ) -> PerDiemRate:
        """Create a per diem rate."""
        rate = PerDiemRate(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(rate)
        await db.commit()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def get_per_diem_rate(
        db: AsyncSession,
        company_id: UUID,
        location_type: str,
        grade_level: Optional[str] = None,
        rate_date: Optional[date] = None
    ) -> Optional[PerDiemRate]:
        """Get applicable per diem rate."""
        if rate_date is None:
            rate_date = date.today()

        query = select(PerDiemRate).where(
            and_(
                PerDiemRate.company_id == company_id,
                PerDiemRate.location_type == location_type,
                PerDiemRate.is_active == True,
                PerDiemRate.effective_from <= rate_date,
                (PerDiemRate.effective_to.is_(None)) | (PerDiemRate.effective_to >= rate_date),
                PerDiemRate.deleted_at.is_(None)
            )
        )

        if grade_level:
            query = query.where(
                (PerDiemRate.grade_level == grade_level) |
                (PerDiemRate.grade_level.is_(None))
            )

        query = query.order_by(PerDiemRate.grade_level.desc().nullsfirst())
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_per_diem_rates(
        db: AsyncSession,
        company_id: UUID,
        location_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PerDiemRate], int]:
        """List per diem rates."""
        query = select(PerDiemRate).where(
            and_(
                PerDiemRate.company_id == company_id,
                PerDiemRate.deleted_at.is_(None)
            )
        )

        if location_type:
            query = query.where(PerDiemRate.location_type == location_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(PerDiemRate.location_type)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    # Mileage Rate Methods
    @staticmethod
    async def create_mileage_rate(
        db: AsyncSession,
        company_id: UUID,
        data: MileageRateCreate
    ) -> MileageRate:
        """Create a mileage rate."""
        rate = MileageRate(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(rate)
        await db.commit()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def get_mileage_rate(
        db: AsyncSession,
        company_id: UUID,
        vehicle_type: str,
        fuel_type: Optional[str] = None,
        rate_date: Optional[date] = None
    ) -> Optional[MileageRate]:
        """Get applicable mileage rate."""
        if rate_date is None:
            rate_date = date.today()

        query = select(MileageRate).where(
            and_(
                MileageRate.company_id == company_id,
                MileageRate.vehicle_type == vehicle_type,
                MileageRate.is_active == True,
                MileageRate.effective_from <= rate_date,
                (MileageRate.effective_to.is_(None)) | (MileageRate.effective_to >= rate_date),
                MileageRate.deleted_at.is_(None)
            )
        )

        if fuel_type:
            query = query.where(
                (MileageRate.fuel_type == fuel_type) |
                (MileageRate.fuel_type.is_(None))
            )

        query = query.order_by(MileageRate.fuel_type.desc().nullsfirst())
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_mileage_rates(
        db: AsyncSession,
        company_id: UUID,
        vehicle_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MileageRate], int]:
        """List mileage rates."""
        query = select(MileageRate).where(
            and_(
                MileageRate.company_id == company_id,
                MileageRate.deleted_at.is_(None)
            )
        )

        if vehicle_type:
            query = query.where(MileageRate.vehicle_type == vehicle_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(MileageRate.vehicle_type)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def calculate_mileage_expense(
        db: AsyncSession,
        company_id: UUID,
        vehicle_type: str,
        distance_km: Decimal,
        fuel_type: Optional[str] = None,
        rate_date: Optional[date] = None
    ) -> Decimal:
        """Calculate mileage expense amount."""
        rate = await PolicyService.get_mileage_rate(
            db, company_id, vehicle_type, fuel_type, rate_date
        )

        if rate:
            return (distance_km * rate.rate_per_km).quantize(Decimal('0.01'))

        return Decimal('0')
