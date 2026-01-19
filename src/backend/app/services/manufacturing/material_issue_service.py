"""Material Issue Service"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import MaterialIssue, MaterialIssueLine
from app.schemas.manufacturing import MaterialIssueCreate


class MaterialIssueService:
    async def get_by_id(
        self, db: AsyncSession, issue_id: UUID, company_id: UUID
    ) -> Optional[MaterialIssue]:
        query = select(MaterialIssue).where(
            MaterialIssue.id == issue_id, MaterialIssue.company_id == company_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_issue_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(MaterialIssue.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"MI-{count + 1:06d}"

    async def create(
        self, db: AsyncSession, company_id: UUID, user_id: UUID, data: MaterialIssueCreate
    ) -> MaterialIssue:
        issue_number = await self._generate_issue_number(db, company_id)
        issue = MaterialIssue(
            id=uuid4(),
            company_id=company_id,
            issue_number=issue_number,
            production_order_id=data.production_order_id,
            issue_date=data.issue_date,
            warehouse_id=data.warehouse_id,
            issued_by=user_id,
            notes=data.notes,
        )
        db.add(issue)

        for line_data in data.lines:
            line = MaterialIssueLine(
                id=uuid4(),
                issue_id=issue.id,
                product_id=line_data.product_id,
                product_variant_id=line_data.product_variant_id,
                batch_id=line_data.batch_id,
                required_quantity=line_data.required_quantity,
                issued_quantity=line_data.issued_quantity,
                uom=line_data.uom,
                notes=line_data.notes,
            )
            db.add(line)

        await db.commit()
        await db.refresh(issue)
        return issue


material_issue_service = MaterialIssueService()
