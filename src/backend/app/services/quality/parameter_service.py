"""Quality Parameter Service"""
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import QualityParameter
from app.schemas.quality import ParameterCreate


class ParameterService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, search: Optional[str], page: int, page_size: int
    ) -> Tuple[List[QualityParameter], int]:
        query = select(QualityParameter).where(
            and_(QualityParameter.company_id == company_id, QualityParameter.deleted_at.is_(None))
        )
        if search:
            query = query.where(
                QualityParameter.name.ilike(f"%{search}%") | QualityParameter.code.ilike(f"%{search}%")
            )
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def create(self, db: AsyncSession, company_id: UUID, data: ParameterCreate) -> QualityParameter:
        param = QualityParameter(
            id=uuid4(), company_id=company_id, code=data.code, name=data.name,
            description=data.description, parameter_type=data.parameter_type, uom=data.uom,
            target_value=data.target_value, upper_limit=data.upper_limit, lower_limit=data.lower_limit,
            is_critical=data.is_critical,
        )
        db.add(param)
        await db.commit()
        await db.refresh(param)
        return param


parameter_service = ParameterService()
