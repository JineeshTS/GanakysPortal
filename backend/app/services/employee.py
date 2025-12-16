"""
Employee service layer.
WBS Reference: Task 3.2.1.2.8
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee


class EmployeeService:
    """Service class for employee operations."""

    @staticmethod
    async def generate_employee_code(db: AsyncSession) -> str:
        """
        Generate unique employee code.

        Format: GCA-YYYY-XXXX (e.g., GCA-2025-0001)

        WBS Reference: Task 3.2.1.2.8
        """
        year = datetime.now().year
        prefix = f"GCA-{year}-"

        # Get the latest employee code for this year
        result = await db.execute(
            select(Employee.employee_code)
            .where(Employee.employee_code.like(f"{prefix}%"))
            .order_by(Employee.employee_code.desc())
            .limit(1)
        )
        latest_code = result.scalar_one_or_none()

        if latest_code:
            # Extract sequence number and increment
            seq = int(latest_code.split("-")[-1]) + 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"

    @staticmethod
    async def get_employee_by_code(
        db: AsyncSession, code: str
    ) -> Optional[Employee]:
        """Get employee by employee code."""
        result = await db.execute(
            select(Employee).where(Employee.employee_code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_employee_by_user_id(
        db: AsyncSession, user_id: str
    ) -> Optional[Employee]:
        """Get employee by user ID."""
        result = await db.execute(
            select(Employee).where(Employee.user_id == user_id)
        )
        return result.scalar_one_or_none()
