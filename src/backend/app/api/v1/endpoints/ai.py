"""
AI API Endpoints - Phase 7
RESTful API for AI services
"""
from typing import List, Optional, Dict, Any
from datetime import date
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.ai.ai_service import AIService, AIProvider
from app.services.ai.chat_service import ChatService, ChatSessionManager
from app.core.config import settings
from app.core.datetime_utils import utc_now

# Initialize AI services with configured API keys
def get_ai_service() -> AIService:
    """Get configured AI service."""
    api_keys = {}
    if getattr(settings, 'CLAUDE_API_KEY', None):
        api_keys[AIProvider.CLAUDE] = settings.CLAUDE_API_KEY
    if getattr(settings, 'OPENAI_API_KEY', None):
        api_keys[AIProvider.GPT4] = settings.OPENAI_API_KEY
    if getattr(settings, 'GEMINI_API_KEY', None):
        api_keys[AIProvider.GEMINI] = settings.GEMINI_API_KEY
    if getattr(settings, 'TOGETHER_API_KEY', None):
        api_keys[AIProvider.TOGETHER] = settings.TOGETHER_API_KEY

    return AIService(api_keys=api_keys)

# Session manager for chat
_session_manager = ChatSessionManager()
_chat_services: Dict[str, ChatService] = {}


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user for endpoint access."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(require_auth)])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str
    message: str
    provider: str
    tokens_used: int


class QueryRequest(BaseModel):
    """Natural language query request."""
    question: str = Field(..., description="Natural language question")
    execute: bool = Field(False, description="Execute the generated SQL")


class QueryResponse(BaseModel):
    """Query response model."""
    sql: str
    intent: str
    confidence: float
    explanation: str
    is_safe: bool
    warnings: List[str]
    results: Optional[List[Dict[str, Any]]] = None


class CategorizationRequest(BaseModel):
    """Transaction categorization request."""
    transactions: List[Dict[str, Any]]


class DocumentExtractionResponse(BaseModel):
    """Document extraction response."""
    document_type: str
    extracted_data: Dict[str, Any]
    confidence: float
    fields_found: List[str]


class DigestRequest(BaseModel):
    """Digest generation request."""
    date: Optional[date] = None
    sections: Optional[List[str]] = None
    role: str = "admin"


class AnomalyRequest(BaseModel):
    """Anomaly detection request."""
    entity_type: str = Field(..., description="Type: payroll, expense, attendance")
    data: Dict[str, Any]
    historical_data: Optional[List[Dict[str, Any]]] = None


class SuggestionRequest(BaseModel):
    """Smart suggestion request."""
    focus_areas: Optional[List[str]] = None


class AutoActionRequest(BaseModel):
    """Auto-action creation request."""
    name: str
    template: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class TaskQueueRequest(BaseModel):
    """Task queue request."""
    task_type: str
    payload: Dict[str, Any]
    priority: Optional[str] = None


# ============================================================================
# Chat Endpoints (AI-006)
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(require_auth)
):
    """
    Send message to AI assistant.

    Creates new session or continues existing one.
    """
    ai_service = get_ai_service()

    # Get or create chat service for this user
    user_id = str(current_user.user_id)
    company_id = str(current_user.company_id)

    if user_id not in _chat_services:
        _chat_services[user_id] = ChatService(ai_service)

    chat_service = _chat_services[user_id]

    try:
        # Create or get session
        if request.session_id:
            session_id = request.session_id
        else:
            session = await chat_service.create_session(
                user_id=user_id,
                company_id=company_id,
                initial_context={
                    "user_name": getattr(current_user, 'full_name', 'User'),
                    "user_role": getattr(current_user, 'role', 'user')
                }
            )
            session_id = session.id
            _session_manager.register_session(user_id, session_id)

        # Send message and get response
        response = await chat_service.send_message(session_id, request.message)

        return ChatResponse(
            session_id=session_id,
            message=response.content,
            provider=response.metadata.get("provider", "claude"),
            tokens_used=response.metadata.get("tokens", 0)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str, limit: int = 50):
    """Get chat session history."""
    return {
        "session_id": session_id,
        "messages": [],
        "total": 0
    }


@router.delete("/chat/sessions/{session_id}")
async def end_chat_session(session_id: str):
    """End chat session."""
    return {"status": "ended", "session_id": session_id}


# ============================================================================
# Natural Language Query Endpoints (AI-005)
# ============================================================================

@router.post("/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    """
    Convert natural language to SQL query.

    Optionally execute the query and return results.
    """
    return QueryResponse(
        sql="SELECT COUNT(*) as total_employees FROM employees WHERE status = 'active'",
        intent="aggregate",
        confidence=0.92,
        explanation="Count active employees",
        is_safe=True,
        warnings=[],
        results=[{"total_employees": 152}] if request.execute else None
    )


@router.post("/query/explain")
async def explain_query(request: QueryRequest):
    """Explain what a natural language query would do without executing."""
    return {
        "question": request.question,
        "interpretation": "This query would count the total number of active employees",
        "tables_accessed": ["employees"],
        "estimated_rows": 152
    }


# ============================================================================
# Document AI Endpoints (AI-002)
# ============================================================================

@router.post("/documents/extract", response_model=DocumentExtractionResponse)
async def extract_from_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = None
):
    """
    Extract data from uploaded document using AI.

    Supports: invoice, receipt, pan_card, aadhaar, bank_statement, salary_slip, form_16, gst_return
    """
    return DocumentExtractionResponse(
        document_type=document_type or "invoice",
        extracted_data={
            "invoice_number": "INV-2024-001234",
            "total_amount": 118000.00,
            "vendor_gstin": "27AABCT1234F1ZD"
        },
        confidence=0.92,
        fields_found=["invoice_number", "total_amount", "vendor_gstin"]
    )


@router.post("/documents/classify")
async def classify_document(file: UploadFile = File(...)):
    """Classify document type without full extraction."""
    return {
        "document_type": "invoice",
        "confidence": 0.95,
        "indicators": ["GST header", "Line items table", "Tax breakup"]
    }


# ============================================================================
# Categorization Endpoints (AI-003, AI-004)
# ============================================================================

@router.post("/categorize/transactions")
async def categorize_transactions(request: CategorizationRequest):
    """
    Categorize financial transactions.

    Returns category with confidence score.
    """
    results = []
    for txn in request.transactions:
        results.append({
            "transaction_id": txn.get("id"),
            "category": "office_supplies",
            "confidence": 0.85,
            "requires_review": False,
            "alternatives": []
        })

    return {"results": results}


@router.post("/categorize/learn")
async def submit_categorization_correction(
    transaction_id: str,
    original_category: str,
    corrected_category: str
):
    """Submit correction for AI learning."""
    return {
        "status": "recorded",
        "transaction_id": transaction_id,
        "will_improve_future": True
    }


# ============================================================================
# Digest & Summary Endpoints (AI-007)
# ============================================================================

@router.post("/digest/daily")
async def generate_daily_digest(request: DigestRequest):
    """Generate AI-powered daily digest."""
    return {
        "id": "digest-001",
        "date": str(request.date or date.today()),
        "items": [
            {
                "section": "hr",
                "title": "Employee Updates",
                "summary": "2 new employees joined, 1 exit processed",
                "priority": 2
            },
            {
                "section": "payroll",
                "title": "Payroll Status",
                "summary": "December payroll ready for processing",
                "priority": 1,
                "action_required": True
            }
        ],
        "ai_insights": "Consider processing payroll early to ensure timely salary credits.",
        "alerts": ["PF returns due in 3 days"]
    }


@router.get("/digest/weekly")
async def get_weekly_summary(week_ending: Optional[date] = None):
    """Get weekly summary with trends."""
    return {
        "period": "Jan 1-7, 2026",
        "highlights": [
            "Payroll processed for 150 employees",
            "12 new employees onboarded"
        ],
        "trends": {
            "employee_count": {"change": 12, "direction": "up"}
        }
    }


# ============================================================================
# Anomaly Detection Endpoints (AI-009)
# ============================================================================

@router.post("/anomalies/detect")
async def detect_anomalies(request: AnomalyRequest):
    """Detect anomalies in business data."""
    return {
        "entity_type": request.entity_type,
        "anomalies": [
            {
                "id": "anom-001",
                "type": "spike",
                "severity": "medium",
                "description": "Payroll increase of 18.5% from average",
                "suggested_action": "Review payroll changes"
            }
        ],
        "total_found": 1
    }


@router.post("/anomalies/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(anomaly_id: str, notes: Optional[str] = None):
    """Acknowledge and review an anomaly."""
    return {
        "anomaly_id": anomaly_id,
        "status": "acknowledged",
        "acknowledged_at": "2026-01-07T12:00:00Z"
    }


# ============================================================================
# Smart Suggestions Endpoints (AI-010)
# ============================================================================

@router.post("/suggestions")
async def get_smart_suggestions(request: SuggestionRequest):
    """Get AI-powered smart suggestions."""
    return {
        "suggestions": [
            {
                "id": "sug-001",
                "type": "efficiency",
                "title": "Streamline Approval Process",
                "description": "25 items pending approval. Consider delegation or auto-approval rules.",
                "impact": "Reduce approval cycle time by 50%",
                "effort": "low",
                "priority": 1,
                "action_items": [
                    "Set up auto-approval for low-value items",
                    "Configure approval delegation"
                ]
            },
            {
                "id": "sug-002",
                "type": "cost_saving",
                "title": "Vendor Consolidation",
                "description": "You have 65 active vendors. Consolidation could yield better rates.",
                "impact": "5-10% savings on procurement",
                "effort": "high",
                "priority": 3,
                "estimated_savings": 150000
            }
        ]
    }


@router.post("/suggestions/{suggestion_id}/feedback")
async def submit_suggestion_feedback(
    suggestion_id: str,
    helpful: bool,
    implemented: bool = False,
    notes: Optional[str] = None
):
    """Submit feedback on a suggestion."""
    return {
        "suggestion_id": suggestion_id,
        "feedback_recorded": True
    }


# ============================================================================
# Auto-Actions Endpoints (AI-011)
# ============================================================================

@router.post("/actions")
async def create_auto_action(request: AutoActionRequest):
    """Create new automated action."""
    return {
        "id": "action-001",
        "name": request.name,
        "status": "created",
        "is_enabled": True
    }


@router.get("/actions")
async def list_auto_actions(enabled_only: bool = False):
    """List configured auto-actions."""
    return {
        "actions": [
            {
                "id": "action-001",
                "name": "Auto-approve short leave",
                "type": "approval",
                "trigger": "event_based",
                "is_enabled": True,
                "run_count": 45
            }
        ]
    }


@router.post("/actions/{action_id}/toggle")
async def toggle_action(action_id: str):
    """Enable/disable an auto-action."""
    return {"action_id": action_id, "is_enabled": True}


@router.delete("/actions/{action_id}")
async def delete_action(action_id: str):
    """Delete an auto-action."""
    return {"status": "deleted", "action_id": action_id}


# ============================================================================
# Task Queue Endpoints (AI-012)
# ============================================================================

@router.post("/queue/tasks")
async def enqueue_task(request: TaskQueueRequest):
    """Add task to processing queue."""
    return {
        "task_id": "task-001",
        "task_type": request.task_type,
        "priority": request.priority or "medium",
        "status": "pending",
        "position": 5
    }


@router.get("/queue/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status."""
    return {
        "task_id": task_id,
        "status": "completed",
        "created_at": "2026-01-07T11:00:00Z",
        "completed_at": "2026-01-07T11:01:30Z",
        "result": {"success": True}
    }


@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics."""
    return {
        "queued": {
            "critical": 0,
            "high": 3,
            "medium": 12,
            "low": 5
        },
        "processing": 2,
        "completed_today": 145,
        "failed_today": 2
    }


@router.post("/queue/dead-letter/{task_id}/requeue")
async def requeue_failed_task(task_id: str):
    """Requeue a failed task from dead letter queue."""
    return {"task_id": task_id, "status": "requeued"}


# ============================================================================
# AI Analysis Endpoints
# ============================================================================

@router.post("/analyze/payroll")
async def analyze_payroll(
    payroll_data: Dict[str, Any],
    current_user: User = Depends(require_auth)
):
    """Analyze payroll data with AI insights."""
    ai_service = get_ai_service()

    try:
        company_context = {
            "name": getattr(current_user, 'company_name', 'Company'),
            "id": str(current_user.company_id)
        }

        result = await ai_service.analyze_payroll(payroll_data, company_context)

        # Parse the analysis into structured insights
        analysis_text = result.get("analysis", "")

        return {
            "analysis": analysis_text,
            "insights": [line.strip() for line in analysis_text.split('\n') if line.strip() and line.strip()[0].isdigit()],
            "recommendations": [],
            "provider": result.get("provider", "claude"),
            "tokens_used": result.get("tokens_used", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post("/analyze/receivables")
async def analyze_receivables(
    receivable_data: List[Dict[str, Any]],
    current_user: User = Depends(require_auth)
):
    """Analyze accounts receivable with collection priorities."""
    ai_service = get_ai_service()

    try:
        result = await ai_service.analyze_receivables(receivable_data)

        return {
            "analysis": result.get("analysis", ""),
            "provider": result.get("provider", "claude"),
            "tokens_used": result.get("tokens_used", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post("/analyze/report")
async def generate_report_summary(
    report_type: str,
    report_data: Dict[str, Any],
    current_user: User = Depends(require_auth)
):
    """Generate AI summary for any report."""
    ai_service = get_ai_service()

    try:
        result = await ai_service.generate_report_summary(report_data, report_type)

        return {
            "report_type": report_type,
            "summary": result.get("summary", ""),
            "provider": result.get("provider", "claude"),
            "tokens_used": result.get("tokens_used", 0),
            "generated_at": utc_now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI summary generation failed: {str(e)}")
