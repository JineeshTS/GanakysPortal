"""Calibration Service"""
from datetime import date, timedelta
from typing import List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import CalibrationRecord
from app.schemas.quality import CalibrationCreate


class CalibrationService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, due_soon: bool, page: int, page_size: int
    ) -> Tuple[List[CalibrationRecord], int]:
        query = select(CalibrationRecord).where(CalibrationRecord.company_id == company_id)
        if due_soon:
            due_date = date.today() + timedelta(days=30)
            query = query.where(CalibrationRecord.next_calibration_date <= due_date)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(CalibrationRecord.next_calibration_date).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def create(self, db: AsyncSession, company_id: UUID, data: CalibrationCreate) -> CalibrationRecord:
        cal = CalibrationRecord(
            id=uuid4(), company_id=company_id, equipment_id=data.equipment_id,
            equipment_name=data.equipment_name, serial_number=data.serial_number,
            location=data.location, calibration_date=data.calibration_date,
            next_calibration_date=data.next_calibration_date,
            calibration_interval_days=data.calibration_interval_days,
            calibrated_by=data.calibrated_by, certificate_number=data.certificate_number,
            result=data.result, notes=data.notes,
        )
        db.add(cal)
        await db.commit()
        await db.refresh(cal)
        return cal


calibration_service = CalibrationService()
