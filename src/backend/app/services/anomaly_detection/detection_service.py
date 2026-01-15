"""
Anomaly Detection Service
Core service for detecting anomalies
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import math

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_detection import (
    AnomalyDetection, AnomalyRule, AnomalyBaseline, AnomalyAlert,
    AnomalyCategory, AnomalySeverity, AnomalyStatus, DetectionMethod
)
from app.schemas.anomaly_detection import (
    AnomalyDetectionUpdate, AnomalyDetectionListResponse, RunDetectionResponse
)


class DetectionService:
    """Service for anomaly detection"""

    async def list_detections(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[AnomalyCategory] = None,
        severity: Optional[AnomalySeverity] = None,
        status: Optional[AnomalyStatus] = None,
        detection_method: Optional[DetectionMethod] = None,
        data_source: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        assigned_to: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> AnomalyDetectionListResponse:
        """List detections with filters and pagination"""
        conditions = [AnomalyDetection.company_id == company_id]

        if category:
            conditions.append(AnomalyDetection.category == category)
        if severity:
            conditions.append(AnomalyDetection.severity == severity)
        if status:
            conditions.append(AnomalyDetection.status == status)
        if detection_method:
            conditions.append(AnomalyDetection.detection_method == detection_method)
        if data_source:
            conditions.append(AnomalyDetection.data_source == data_source)
        if entity_type:
            conditions.append(AnomalyDetection.entity_type == entity_type)
        if entity_id:
            conditions.append(AnomalyDetection.entity_id == entity_id)
        if start_date:
            conditions.append(AnomalyDetection.anomaly_date >= start_date)
        if end_date:
            conditions.append(AnomalyDetection.anomaly_date <= end_date)
        if assigned_to:
            conditions.append(AnomalyDetection.assigned_to == assigned_to)

        # Get total count
        count_query = select(func.count()).select_from(AnomalyDetection).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Calculate pagination
        pages = math.ceil(total / page_size) if total > 0 else 1
        skip = (page - 1) * page_size

        # Get items
        query = (
            select(AnomalyDetection)
            .where(and_(*conditions))
            .order_by(AnomalyDetection.detected_at.desc())
            .offset(skip)
            .limit(page_size)
        )
        result = await db.execute(query)
        detections = result.scalars().all()

        return AnomalyDetectionListResponse(
            items=list(detections),
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )

    async def get_detection(
        self,
        db: AsyncSession,
        detection_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyDetection]:
        """Get a specific detection"""
        query = select(AnomalyDetection).where(
            and_(
                AnomalyDetection.id == detection_id,
                AnomalyDetection.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_detection(
        self,
        db: AsyncSession,
        detection_id: UUID,
        company_id: UUID,
        user_id: UUID,
        detection_data: AnomalyDetectionUpdate
    ) -> Optional[AnomalyDetection]:
        """Update a detection"""
        detection = await self.get_detection(db, detection_id, company_id)
        if not detection:
            return None

        update_data = detection_data.model_dump(exclude_unset=True)

        # Handle status changes
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == AnomalyStatus.investigating and not detection.investigated_at:
                detection.investigated_at = datetime.utcnow()
            elif new_status == AnomalyStatus.resolved and not detection.resolved_at:
                detection.resolved_at = datetime.utcnow()

        for field, value in update_data.items():
            setattr(detection, field, value)

        detection.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(detection)
        return detection

    async def assign_detection(
        self,
        db: AsyncSession,
        detection_id: UUID,
        company_id: UUID,
        assignee_id: UUID
    ) -> Optional[AnomalyDetection]:
        """Assign a detection to a user"""
        detection = await self.get_detection(db, detection_id, company_id)
        if not detection:
            return None

        detection.assigned_to = assignee_id
        detection.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(detection)
        return detection

    async def update_status(
        self,
        db: AsyncSession,
        detection_id: UUID,
        company_id: UUID,
        user_id: UUID,
        new_status: AnomalyStatus
    ) -> Optional[AnomalyDetection]:
        """Update detection status"""
        detection = await self.get_detection(db, detection_id, company_id)
        if not detection:
            return None

        detection.status = new_status
        detection.updated_at = datetime.utcnow()

        if new_status == AnomalyStatus.investigating:
            detection.investigated_at = datetime.utcnow()
        elif new_status == AnomalyStatus.resolved:
            detection.resolved_at = datetime.utcnow()

        await db.commit()
        await db.refresh(detection)
        return detection

    async def resolve_detection(
        self,
        db: AsyncSession,
        detection_id: UUID,
        company_id: UUID,
        user_id: UUID,
        resolution_notes: Optional[str] = None,
        root_cause: Optional[str] = None,
        corrective_action: Optional[str] = None
    ) -> Optional[AnomalyDetection]:
        """Resolve a detection"""
        detection = await self.get_detection(db, detection_id, company_id)
        if not detection:
            return None

        detection.status = AnomalyStatus.resolved
        detection.resolved_at = datetime.utcnow()
        detection.updated_at = datetime.utcnow()

        if resolution_notes:
            detection.resolution_notes = resolution_notes
        if root_cause:
            detection.root_cause = root_cause
        if corrective_action:
            detection.corrective_action = corrective_action

        await db.commit()
        await db.refresh(detection)
        return detection

    async def _generate_detection_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate unique detection number"""
        year = datetime.utcnow().year
        prefix = f"ANM-{year}"

        # Count existing detections this year
        count_query = select(func.count()).select_from(AnomalyDetection).where(
            and_(
                AnomalyDetection.company_id == company_id,
                AnomalyDetection.detection_number.like(f"{prefix}%")
            )
        )
        count = await db.scalar(count_query) or 0

        return f"{prefix}-{count + 1:06d}"

    async def create_detection(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: AnomalyCategory,
        severity: AnomalySeverity,
        detection_method: DetectionMethod,
        title: str,
        data_source: str,
        anomaly_date: date,
        description: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        entity_name: Optional[str] = None,
        metric_name: Optional[str] = None,
        observed_value: Optional[float] = None,
        expected_value: Optional[float] = None,
        deviation: Optional[float] = None,
        deviation_type: Optional[str] = None,
        confidence_score: Optional[float] = None,
        anomaly_score: Optional[float] = None,
        context_data: Optional[Dict[str, Any]] = None,
        comparison_data: Optional[Dict[str, Any]] = None,
        rule_id: Optional[UUID] = None,
        baseline_id: Optional[UUID] = None,
        model_id: Optional[UUID] = None
    ) -> AnomalyDetection:
        """Create a new detection"""
        detection_number = await self._generate_detection_number(db, company_id)

        detection = AnomalyDetection(
            company_id=company_id,
            detection_number=detection_number,
            category=category,
            severity=severity,
            status=AnomalyStatus.pending,
            detection_method=detection_method,
            title=title,
            description=description,
            data_source=data_source,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            metric_name=metric_name,
            observed_value=observed_value,
            expected_value=expected_value,
            deviation=deviation,
            deviation_type=deviation_type,
            confidence_score=confidence_score,
            anomaly_score=anomaly_score,
            context_data=context_data,
            comparison_data=comparison_data,
            anomaly_date=anomaly_date,
            rule_id=rule_id,
            baseline_id=baseline_id,
            model_id=model_id
        )

        db.add(detection)
        await db.commit()
        await db.refresh(detection)

        # Create alert if rule has alerting enabled
        if rule_id:
            rule_query = select(AnomalyRule).where(AnomalyRule.id == rule_id)
            rule_result = await db.execute(rule_query)
            rule = rule_result.scalar_one_or_none()

            if rule and rule.alert_enabled:
                alert = AnomalyAlert(
                    company_id=company_id,
                    detection_id=detection.id,
                    rule_id=rule_id,
                    title=f"Anomaly Detected: {title}",
                    message=description,
                    severity=severity,
                    recipients=rule.alert_recipients
                )
                db.add(alert)
                await db.commit()

        return detection

    async def run_detection(
        self,
        db: AsyncSession,
        company_id: UUID,
        rule_ids: Optional[List[UUID]] = None,
        category: Optional[AnomalyCategory] = None,
        data_source: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> RunDetectionResponse:
        """Run anomaly detection"""
        job_id = str(uuid4())
        started_at = datetime.utcnow()
        rules_executed = 0
        detections_created = 0
        errors = []

        # Get rules to execute
        conditions = [AnomalyRule.company_id == company_id, AnomalyRule.is_active == True]
        if rule_ids:
            conditions.append(AnomalyRule.id.in_(rule_ids))
        if category:
            conditions.append(AnomalyRule.category == category)
        if data_source:
            conditions.append(AnomalyRule.data_source == data_source)

        query = select(AnomalyRule).where(and_(*conditions))
        result = await db.execute(query)
        rules = result.scalars().all()

        for rule in rules:
            try:
                # In production, this would:
                # 1. Fetch data from the rule's data source
                # 2. Apply rule conditions
                # 3. Compare against baselines
                # 4. Create detections for anomalies found
                rules_executed += 1

                # Placeholder: In production, detect anomalies here
                # detections_created += await self._detect_anomalies_for_rule(
                #     db, company_id, rule, start_date, end_date
                # )

            except Exception as e:
                errors.append(f"Rule {rule.code}: {str(e)}")

        return RunDetectionResponse(
            job_id=job_id,
            rules_executed=rules_executed,
            detections_created=detections_created,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            status="completed" if not errors else "completed_with_errors",
            errors=errors
        )

    async def detect_statistical_anomaly(
        self,
        observed_value: float,
        baseline: AnomalyBaseline,
        threshold_std_devs: float = 3.0
    ) -> Optional[Dict[str, Any]]:
        """Detect anomaly using statistical method (z-score)"""
        if not baseline.mean_value or not baseline.std_deviation:
            return None

        if baseline.std_deviation == 0:
            return None

        z_score = abs(observed_value - baseline.mean_value) / baseline.std_deviation

        if z_score > threshold_std_devs:
            deviation = observed_value - baseline.mean_value
            deviation_pct = (deviation / baseline.mean_value * 100) if baseline.mean_value else 0

            return {
                "is_anomaly": True,
                "z_score": z_score,
                "deviation": deviation,
                "deviation_pct": deviation_pct,
                "expected_value": baseline.mean_value,
                "confidence_score": min(0.99, 0.5 + (z_score - threshold_std_devs) * 0.1)
            }

        return {"is_anomaly": False}


detection_service = DetectionService()
