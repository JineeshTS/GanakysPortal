"""
AI Anomaly Detection API Endpoints
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.anomaly_detection import (
    AnomalyCategory, AnomalySeverity, AnomalyStatus,
    DetectionMethod, FeedbackType, ModelStatus
)
from app.schemas.anomaly_detection import (
    AnomalyRuleCreate, AnomalyRuleUpdate, AnomalyRuleResponse, AnomalyRuleListResponse,
    AnomalyBaselineResponse,
    AnomalyDetectionCreate, AnomalyDetectionUpdate, AnomalyDetectionResponse, AnomalyDetectionListResponse,
    AnomalyPatternResponse,
    AnomalyModelCreate, AnomalyModelUpdate, AnomalyModelResponse, AnomalyModelListResponse,
    AnomalyAlertResponse, AnomalyAlertListResponse,
    AnomalyFeedbackCreate, AnomalyFeedbackResponse,
    AnomalyDashboardMetrics,
    RunDetectionRequest, RunDetectionResponse,
    CalculateBaselineRequest, TrainModelRequest
)

router = APIRouter()


# ============ Rules Endpoints ============

@router.get("/rules", response_model=AnomalyRuleListResponse)
async def list_rules(
    category: Optional[AnomalyCategory] = None,
    data_source: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List anomaly detection rules"""
    from app.services.anomaly_detection import rule_service

    rules, total = await rule_service.list_rules(
        db=db,
        company_id=current_user.company_id,
        category=category,
        data_source=data_source,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return AnomalyRuleListResponse(items=rules, total=total)


@router.post("/rules", response_model=AnomalyRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_in: AnomalyRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new anomaly detection rule"""
    from app.services.anomaly_detection import rule_service

    rule = await rule_service.create_rule(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        rule_data=rule_in
    )
    return rule


@router.get("/rules/{rule_id}", response_model=AnomalyRuleResponse)
async def get_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific rule"""
    from app.services.anomaly_detection import rule_service

    rule = await rule_service.get_rule(db=db, rule_id=rule_id, company_id=current_user.company_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch("/rules/{rule_id}", response_model=AnomalyRuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_in: AnomalyRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a rule"""
    from app.services.anomaly_detection import rule_service

    rule = await rule_service.update_rule(
        db=db,
        rule_id=rule_id,
        company_id=current_user.company_id,
        rule_data=rule_in
    )
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a rule"""
    from app.services.anomaly_detection import rule_service

    deleted = await rule_service.delete_rule(db=db, rule_id=rule_id, company_id=current_user.company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")


@router.post("/rules/{rule_id}/toggle", response_model=AnomalyRuleResponse)
async def toggle_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle rule active status"""
    from app.services.anomaly_detection import rule_service

    rule = await rule_service.toggle_rule(db=db, rule_id=rule_id, company_id=current_user.company_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


# ============ Baselines Endpoints ============

@router.get("/baselines", response_model=List[AnomalyBaselineResponse])
async def list_baselines(
    rule_id: Optional[UUID] = None,
    data_source: Optional[str] = None,
    metric_name: Optional[str] = None,
    is_current: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List computed baselines"""
    from app.services.anomaly_detection import baseline_service

    baselines = await baseline_service.list_baselines(
        db=db,
        company_id=current_user.company_id,
        rule_id=rule_id,
        data_source=data_source,
        metric_name=metric_name,
        is_current=is_current,
        skip=skip,
        limit=limit
    )
    return baselines


@router.post("/baselines/calculate", response_model=dict)
async def calculate_baselines(
    request: CalculateBaselineRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate baselines for specified rules/metrics"""
    from app.services.anomaly_detection import baseline_service

    result = await baseline_service.calculate_baselines(
        db=db,
        company_id=current_user.company_id,
        rule_id=request.rule_id,
        data_source=request.data_source,
        metric_name=request.metric_name,
        period_days=request.period_days
    )
    return result


@router.get("/baselines/{baseline_id}", response_model=AnomalyBaselineResponse)
async def get_baseline(
    baseline_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific baseline"""
    from app.services.anomaly_detection import baseline_service

    baseline = await baseline_service.get_baseline(
        db=db, baseline_id=baseline_id, company_id=current_user.company_id
    )
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
    return baseline


# ============ Detections Endpoints ============

@router.get("/detections", response_model=AnomalyDetectionListResponse)
async def list_detections(
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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List anomaly detections with filters"""
    from app.services.anomaly_detection import detection_service

    result = await detection_service.list_detections(
        db=db,
        company_id=current_user.company_id,
        category=category,
        severity=severity,
        status=status,
        detection_method=detection_method,
        data_source=data_source,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        assigned_to=assigned_to,
        page=page,
        page_size=page_size
    )
    return result


@router.get("/detections/{detection_id}", response_model=AnomalyDetectionResponse)
async def get_detection(
    detection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific detection"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.get_detection(
        db=db, detection_id=detection_id, company_id=current_user.company_id
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.patch("/detections/{detection_id}", response_model=AnomalyDetectionResponse)
async def update_detection(
    detection_id: UUID,
    detection_in: AnomalyDetectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a detection (status, assignment, investigation notes, etc.)"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.update_detection(
        db=db,
        detection_id=detection_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        detection_data=detection_in
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.post("/detections/{detection_id}/assign", response_model=AnomalyDetectionResponse)
async def assign_detection(
    detection_id: UUID,
    assignee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a detection to a user"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.assign_detection(
        db=db,
        detection_id=detection_id,
        company_id=current_user.company_id,
        assignee_id=assignee_id
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.post("/detections/{detection_id}/confirm", response_model=AnomalyDetectionResponse)
async def confirm_detection(
    detection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm an anomaly as true positive"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.update_status(
        db=db,
        detection_id=detection_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        new_status=AnomalyStatus.confirmed
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.post("/detections/{detection_id}/dismiss", response_model=AnomalyDetectionResponse)
async def dismiss_detection(
    detection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss an anomaly as false positive"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.update_status(
        db=db,
        detection_id=detection_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        new_status=AnomalyStatus.false_positive
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.post("/detections/{detection_id}/resolve", response_model=AnomalyDetectionResponse)
async def resolve_detection(
    detection_id: UUID,
    resolution_notes: Optional[str] = None,
    root_cause: Optional[str] = None,
    corrective_action: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve an anomaly"""
    from app.services.anomaly_detection import detection_service

    detection = await detection_service.resolve_detection(
        db=db,
        detection_id=detection_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        resolution_notes=resolution_notes,
        root_cause=root_cause,
        corrective_action=corrective_action
    )
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.post("/run", response_model=RunDetectionResponse)
async def run_detection(
    request: RunDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run anomaly detection manually"""
    from app.services.anomaly_detection import detection_service

    result = await detection_service.run_detection(
        db=db,
        company_id=current_user.company_id,
        rule_ids=request.rule_ids,
        category=request.category,
        data_source=request.data_source,
        start_date=request.start_date,
        end_date=request.end_date
    )
    return result


# ============ Patterns Endpoints ============

@router.get("/patterns", response_model=List[AnomalyPatternResponse])
async def list_patterns(
    pattern_type: Optional[str] = None,
    data_source: Optional[str] = None,
    metric_name: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List learned patterns"""
    from app.services.anomaly_detection import pattern_service

    patterns = await pattern_service.list_patterns(
        db=db,
        company_id=current_user.company_id,
        pattern_type=pattern_type,
        data_source=data_source,
        metric_name=metric_name,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return patterns


@router.get("/patterns/{pattern_id}", response_model=AnomalyPatternResponse)
async def get_pattern(
    pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific pattern"""
    from app.services.anomaly_detection import pattern_service

    pattern = await pattern_service.get_pattern(
        db=db, pattern_id=pattern_id, company_id=current_user.company_id
    )
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern


@router.post("/patterns/learn", response_model=dict)
async def learn_patterns(
    data_source: str,
    metric_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Learn patterns from historical data"""
    from app.services.anomaly_detection import pattern_service

    result = await pattern_service.learn_patterns(
        db=db,
        company_id=current_user.company_id,
        data_source=data_source,
        metric_name=metric_name
    )
    return result


# ============ Models Endpoints ============

@router.get("/models", response_model=AnomalyModelListResponse)
async def list_models(
    model_type: Optional[str] = None,
    status: Optional[ModelStatus] = None,
    data_source: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ML models"""
    from app.services.anomaly_detection import model_service

    models, total = await model_service.list_models(
        db=db,
        company_id=current_user.company_id,
        model_type=model_type,
        status=status,
        data_source=data_source,
        skip=skip,
        limit=limit
    )
    return AnomalyModelListResponse(items=models, total=total)


@router.post("/models", response_model=AnomalyModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_in: AnomalyModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ML model"""
    from app.services.anomaly_detection import model_service

    model = await model_service.create_model(
        db=db,
        company_id=current_user.company_id,
        model_data=model_in
    )
    return model


@router.get("/models/{model_id}", response_model=AnomalyModelResponse)
async def get_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific model"""
    from app.services.anomaly_detection import model_service

    model = await model_service.get_model(
        db=db, model_id=model_id, company_id=current_user.company_id
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.patch("/models/{model_id}", response_model=AnomalyModelResponse)
async def update_model(
    model_id: UUID,
    model_in: AnomalyModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a model"""
    from app.services.anomaly_detection import model_service

    model = await model_service.update_model(
        db=db,
        model_id=model_id,
        company_id=current_user.company_id,
        model_data=model_in
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a model"""
    from app.services.anomaly_detection import model_service

    deleted = await model_service.delete_model(
        db=db, model_id=model_id, company_id=current_user.company_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Model not found")


@router.post("/models/{model_id}/train", response_model=AnomalyModelResponse)
async def train_model(
    model_id: UUID,
    training_start_date: Optional[date] = None,
    training_end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train a model"""
    from app.services.anomaly_detection import model_service

    model = await model_service.train_model(
        db=db,
        model_id=model_id,
        company_id=current_user.company_id,
        training_start_date=training_start_date,
        training_end_date=training_end_date
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/models/train-new", response_model=AnomalyModelResponse)
async def train_new_model(
    request: TrainModelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create and train a new model"""
    from app.services.anomaly_detection import model_service

    model = await model_service.create_and_train_model(
        db=db,
        company_id=current_user.company_id,
        request=request
    )
    return model


# ============ Alerts Endpoints ============

@router.get("/alerts", response_model=AnomalyAlertListResponse)
async def list_alerts(
    severity: Optional[AnomalySeverity] = None,
    is_read: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List alerts"""
    from app.services.anomaly_detection import alert_service

    result = await alert_service.list_alerts(
        db=db,
        company_id=current_user.company_id,
        severity=severity,
        is_read=is_read,
        skip=skip,
        limit=limit
    )
    return result


@router.get("/alerts/{alert_id}", response_model=AnomalyAlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific alert"""
    from app.services.anomaly_detection import alert_service

    alert = await alert_service.get_alert(
        db=db, alert_id=alert_id, company_id=current_user.company_id
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/read", response_model=AnomalyAlertResponse)
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an alert as read"""
    from app.services.anomaly_detection import alert_service

    alert = await alert_service.mark_read(
        db=db, alert_id=alert_id, company_id=current_user.company_id
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/mark-all-read", response_model=dict)
async def mark_all_alerts_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all alerts as read"""
    from app.services.anomaly_detection import alert_service

    count = await alert_service.mark_all_read(db=db, company_id=current_user.company_id)
    return {"marked_read": count}


# ============ Feedback Endpoints ============

@router.post("/feedback", response_model=AnomalyFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_in: AnomalyFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback on a detection"""
    from app.services.anomaly_detection import feedback_service

    feedback = await feedback_service.submit_feedback(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        feedback_data=feedback_in
    )
    return feedback


@router.get("/feedback", response_model=List[AnomalyFeedbackResponse])
async def list_feedback(
    detection_id: Optional[UUID] = None,
    feedback_type: Optional[FeedbackType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List feedback"""
    from app.services.anomaly_detection import feedback_service

    feedbacks = await feedback_service.list_feedback(
        db=db,
        company_id=current_user.company_id,
        detection_id=detection_id,
        feedback_type=feedback_type,
        skip=skip,
        limit=limit
    )
    return feedbacks


# ============ Dashboard Endpoint ============

@router.get("/dashboard", response_model=AnomalyDashboardMetrics)
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get anomaly detection dashboard metrics"""
    from app.services.anomaly_detection import dashboard_service

    metrics = await dashboard_service.get_dashboard_metrics(
        db=db,
        company_id=current_user.company_id,
        days=days
    )
    return metrics
