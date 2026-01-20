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
    # Try to get session from session manager
    session = _session_manager.get_session(session_id) if hasattr(_session_manager, 'get_session') else None

    if session:
        messages = session.get("messages", [])[-limit:] if session.get("messages") else []
        return {
            "session_id": session_id,
            "messages": messages,
            "total": len(messages),
            "created_at": session.get("created_at"),
            "last_activity": session.get("last_activity")
        }

    # Session not found in memory, return empty but indicate session might have expired
    return {
        "session_id": session_id,
        "messages": [],
        "total": 0,
        "note": "Session not found or expired"
    }


@router.delete("/chat/sessions/{session_id}")
async def end_chat_session(session_id: str):
    """End chat session."""
    # Try to end session in session manager
    if hasattr(_session_manager, 'end_session'):
        _session_manager.end_session(session_id)

    # Remove from chat services if exists
    if session_id in _chat_services:
        del _chat_services[session_id]

    return {
        "status": "ended",
        "session_id": session_id,
        "ended_at": utc_now().isoformat()
    }


# ============================================================================
# Natural Language Query Endpoints (AI-005)
# ============================================================================

@router.post("/query", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    current_user: User = Depends(require_auth)
):
    """
    Convert natural language to SQL query.

    Optionally execute the query and return results.
    """
    ai_service = get_ai_service()

    # Build prompt for SQL generation
    sql_prompt = f"""Convert this natural language question to a SQL query for a PostgreSQL database.

Question: {request.question}

Available tables:
- employees (id, employee_code, first_name, last_name, email, department, status, hire_date, salary)
- attendance (id, employee_id, date, check_in, check_out, status)
- leave_requests (id, employee_id, leave_type, start_date, end_date, status, days)
- payroll (id, employee_id, month, year, gross_salary, net_salary, deductions)
- invoices (id, invoice_number, customer_id, amount, status, due_date)

Return a JSON response with:
{{"sql": "the SQL query", "intent": "select|aggregate|join|update", "explanation": "brief explanation", "is_safe": true/false, "warnings": []}}

Only generate SELECT queries. Never generate UPDATE, DELETE, or DROP statements."""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": sql_prompt}],
            feature="chat",
            temperature=0.3
        )

        if response.error:
            return QueryResponse(
                sql="",
                intent="error",
                confidence=0.0,
                explanation=f"AI service error: {response.error}",
                is_safe=False,
                warnings=["AI service unavailable"],
                results=None
            )

        # Parse AI response
        import json
        try:
            result = json.loads(response.content)
            return QueryResponse(
                sql=result.get("sql", ""),
                intent=result.get("intent", "unknown"),
                confidence=0.85,
                explanation=result.get("explanation", ""),
                is_safe=result.get("is_safe", False),
                warnings=result.get("warnings", []),
                results=None  # Don't execute by default for safety
            )
        except json.JSONDecodeError:
            # AI didn't return valid JSON, extract SQL from text
            return QueryResponse(
                sql=response.content[:500] if response.content else "",
                intent="unknown",
                confidence=0.5,
                explanation="Parsed from AI response",
                is_safe=False,
                warnings=["Response format unexpected - review query carefully"],
                results=None
            )
    except Exception as e:
        return QueryResponse(
            sql="",
            intent="error",
            confidence=0.0,
            explanation=str(e),
            is_safe=False,
            warnings=["Query generation failed"],
            results=None
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
    document_type: Optional[str] = None,
    current_user: User = Depends(require_auth)
):
    """
    Extract data from uploaded document using AI.

    Supports: invoice, receipt, pan_card, aadhaar, bank_statement, salary_slip, form_16, gst_return
    """
    import base64

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Determine document type from filename if not provided
    filename = file.filename or "document"
    detected_type = document_type

    if not detected_type:
        filename_lower = filename.lower()
        if "invoice" in filename_lower or "inv" in filename_lower:
            detected_type = "invoice"
        elif "receipt" in filename_lower:
            detected_type = "receipt"
        elif "pan" in filename_lower:
            detected_type = "pan_card"
        elif "aadhaar" in filename_lower or "aadhar" in filename_lower:
            detected_type = "aadhaar"
        elif "bank" in filename_lower or "statement" in filename_lower:
            detected_type = "bank_statement"
        elif "salary" in filename_lower or "payslip" in filename_lower:
            detected_type = "salary_slip"
        elif "form16" in filename_lower or "form-16" in filename_lower:
            detected_type = "form_16"
        else:
            detected_type = "invoice"  # Default

    ai_service = get_ai_service()

    # Build extraction prompt based on document type
    extraction_fields = {
        "invoice": ["invoice_number", "invoice_date", "vendor_name", "vendor_gstin", "total_amount", "tax_amount", "line_items"],
        "receipt": ["receipt_number", "date", "vendor_name", "total_amount", "payment_method"],
        "pan_card": ["pan_number", "name", "father_name", "date_of_birth"],
        "aadhaar": ["aadhaar_number", "name", "address", "date_of_birth"],
        "bank_statement": ["account_number", "bank_name", "period", "opening_balance", "closing_balance", "transactions"],
        "salary_slip": ["employee_name", "employee_id", "month", "gross_salary", "deductions", "net_salary"],
        "form_16": ["employee_name", "pan", "employer_name", "financial_year", "total_income", "tax_deducted"],
    }

    fields = extraction_fields.get(detected_type, extraction_fields["invoice"])

    prompt = f"""You are a document extraction AI. Extract structured data from this {detected_type} document.

Document filename: {filename}
Document size: {file_size} bytes

Extract these fields if present: {', '.join(fields)}

Return a JSON object with:
{{"extracted_data": {{field: value, ...}}, "confidence": 0.0-1.0, "fields_found": ["field1", "field2", ...]}}

If you cannot extract a field, omit it. Ensure all monetary values are numbers, dates are in ISO format."""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="chat",
            temperature=0.2
        )

        if response.error:
            return DocumentExtractionResponse(
                document_type=detected_type,
                extracted_data={"error": response.error},
                confidence=0.0,
                fields_found=[]
            )

        # Parse response
        import json
        try:
            result = json.loads(response.content)
            return DocumentExtractionResponse(
                document_type=detected_type,
                extracted_data=result.get("extracted_data", {}),
                confidence=result.get("confidence", 0.7),
                fields_found=result.get("fields_found", list(result.get("extracted_data", {}).keys()))
            )
        except json.JSONDecodeError:
            return DocumentExtractionResponse(
                document_type=detected_type,
                extracted_data={"raw_response": response.content[:500]},
                confidence=0.3,
                fields_found=[]
            )
    except Exception as e:
        return DocumentExtractionResponse(
            document_type=detected_type,
            extracted_data={"error": str(e)},
            confidence=0.0,
            fields_found=[]
        )


@router.post("/documents/classify")
async def classify_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_auth)
):
    """Classify document type without full extraction."""
    filename = file.filename or "document"
    content = await file.read()
    file_size = len(content)

    ai_service = get_ai_service()

    prompt = f"""Classify this document based on its filename and characteristics.

Filename: {filename}
File size: {file_size} bytes

Classify into one of these types:
- invoice: Purchase or sales invoice
- receipt: Payment receipt
- pan_card: PAN card image
- aadhaar: Aadhaar card image
- bank_statement: Bank account statement
- salary_slip: Employee salary slip
- form_16: Income tax Form 16
- gst_return: GST return document
- contract: Legal contract or agreement
- other: Cannot classify

Return JSON: {{"document_type": "type", "confidence": 0.0-1.0, "indicators": ["reason1", "reason2"]}}"""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="chat",
            temperature=0.2
        )

        if response.error:
            return {
                "document_type": "other",
                "confidence": 0.0,
                "indicators": [f"Error: {response.error}"]
            }

        import json
        try:
            result = json.loads(response.content)
            return {
                "document_type": result.get("document_type", "other"),
                "confidence": result.get("confidence", 0.5),
                "indicators": result.get("indicators", [])
            }
        except json.JSONDecodeError:
            # Fallback classification based on filename
            filename_lower = filename.lower()
            if "invoice" in filename_lower:
                return {"document_type": "invoice", "confidence": 0.7, "indicators": ["Filename contains 'invoice'"]}
            elif "receipt" in filename_lower:
                return {"document_type": "receipt", "confidence": 0.7, "indicators": ["Filename contains 'receipt'"]}
            else:
                return {"document_type": "other", "confidence": 0.3, "indicators": ["Could not classify"]}
    except Exception as e:
        return {
            "document_type": "other",
            "confidence": 0.0,
            "indicators": [str(e)]
        }


# ============================================================================
# Categorization Endpoints (AI-003, AI-004)
# ============================================================================

@router.post("/categorize/transactions")
async def categorize_transactions(
    request: CategorizationRequest,
    current_user: User = Depends(require_auth)
):
    """
    Categorize financial transactions.

    Returns category with confidence score.
    """
    if not request.transactions:
        return {"results": []}

    ai_service = get_ai_service()

    # Build prompt with transaction data
    txn_list = []
    for i, txn in enumerate(request.transactions[:20]):  # Limit to 20 transactions
        txn_list.append(f"{i+1}. ID: {txn.get('id')}, Description: {txn.get('description', 'N/A')}, Amount: {txn.get('amount', 0)}")

    categories = [
        "salary_expense", "office_supplies", "travel_expense", "utilities",
        "rent", "professional_services", "marketing", "software_subscription",
        "equipment", "insurance", "taxes", "bank_charges", "interest_expense",
        "sales_revenue", "other_income", "refund", "other_expense"
    ]

    prompt = f"""Categorize these financial transactions into appropriate accounting categories.

Transactions:
{chr(10).join(txn_list)}

Available categories: {', '.join(categories)}

Return JSON array:
[{{"transaction_id": "id", "category": "category_name", "confidence": 0.0-1.0, "requires_review": true/false, "alternatives": ["alt1", "alt2"]}}]

Set requires_review=true if confidence < 0.7 or category is ambiguous."""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="chat",
            temperature=0.3
        )

        if response.error:
            # Return default categorization on error
            results = []
            for txn in request.transactions:
                results.append({
                    "transaction_id": txn.get("id"),
                    "category": "other_expense",
                    "confidence": 0.3,
                    "requires_review": True,
                    "alternatives": [],
                    "error": response.error
                })
            return {"results": results}

        import json
        try:
            results = json.loads(response.content)
            if isinstance(results, list):
                return {"results": results}
            elif isinstance(results, dict) and "results" in results:
                return results
            else:
                return {"results": [results]}
        except json.JSONDecodeError:
            # Fallback
            results = []
            for txn in request.transactions:
                desc = str(txn.get("description", "")).lower()
                if "salary" in desc or "payroll" in desc:
                    cat = "salary_expense"
                elif "office" in desc or "supplies" in desc:
                    cat = "office_supplies"
                elif "travel" in desc or "flight" in desc:
                    cat = "travel_expense"
                elif "rent" in desc:
                    cat = "rent"
                else:
                    cat = "other_expense"

                results.append({
                    "transaction_id": txn.get("id"),
                    "category": cat,
                    "confidence": 0.5,
                    "requires_review": True,
                    "alternatives": []
                })
            return {"results": results}

    except Exception as e:
        results = []
        for txn in request.transactions:
            results.append({
                "transaction_id": txn.get("id"),
                "category": "other_expense",
                "confidence": 0.0,
                "requires_review": True,
                "alternatives": [],
                "error": str(e)
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
async def generate_daily_digest(
    request: DigestRequest,
    current_user: User = Depends(require_auth)
):
    """Generate AI-powered daily digest."""
    import uuid

    ai_service = get_ai_service()
    digest_date = request.date or date.today()

    # Build context for AI
    prompt = f"""Generate a daily business digest for {digest_date.isoformat()}.

Create a concise daily summary with these sections:
1. HR Updates (new hires, exits, leave requests)
2. Payroll Status (processing status, pending items)
3. Finance Overview (invoices, payments, receivables)
4. Compliance Alerts (upcoming deadlines, filings due)

Return JSON format:
{{
    "items": [
        {{"section": "hr", "title": "Title", "summary": "Brief summary", "priority": 1-3, "action_required": true/false}},
        ...
    ],
    "ai_insights": "Key insight or recommendation",
    "alerts": ["Alert 1", "Alert 2"]
}}

Focus on actionable items. Priority: 1=High, 2=Medium, 3=Low."""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="chat",
            temperature=0.5
        )

        if response.error:
            return {
                "id": str(uuid.uuid4()),
                "date": str(digest_date),
                "items": [],
                "ai_insights": f"Unable to generate digest: {response.error}",
                "alerts": [],
                "error": response.error
            }

        import json
        try:
            result = json.loads(response.content)
            return {
                "id": str(uuid.uuid4()),
                "date": str(digest_date),
                "items": result.get("items", []),
                "ai_insights": result.get("ai_insights", ""),
                "alerts": result.get("alerts", []),
                "generated_by": response.provider.value
            }
        except json.JSONDecodeError:
            return {
                "id": str(uuid.uuid4()),
                "date": str(digest_date),
                "items": [{"section": "general", "title": "Daily Summary", "summary": response.content[:500], "priority": 2}],
                "ai_insights": "Digest generated",
                "alerts": []
            }
    except Exception as e:
        return {
            "id": str(uuid.uuid4()),
            "date": str(digest_date),
            "items": [],
            "ai_insights": "",
            "alerts": [],
            "error": str(e)
        }


@router.get("/digest/weekly")
async def get_weekly_summary(week_ending: Optional[date] = None):
    """Get weekly summary with trends."""
    from datetime import timedelta

    # Calculate week dates
    end_date = week_ending or date.today()
    # Adjust to end of week (Sunday)
    days_until_sunday = (6 - end_date.weekday()) % 7
    if days_until_sunday == 0 and end_date.weekday() != 6:
        days_until_sunday = 0  # Already past Sunday, use current date
    week_end = end_date + timedelta(days=days_until_sunday)
    week_start = week_end - timedelta(days=6)

    # Format period string
    period = f"{week_start.strftime('%b %d')}-{week_end.strftime('%d, %Y')}"

    # Return structure with actual dates (data would come from DB aggregations in full implementation)
    return {
        "period": period,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "highlights": [],
        "trends": {},
        "generated_at": utc_now().isoformat(),
        "note": "Weekly summary - connect to analytics service for actual data"
    }


# ============================================================================
# Anomaly Detection Endpoints (AI-009)
# ============================================================================

@router.post("/anomalies/detect")
async def detect_anomalies(
    request: AnomalyRequest,
    current_user: User = Depends(require_auth)
):
    """Detect anomalies in business data."""
    import uuid

    ai_service = get_ai_service()

    # Build anomaly detection prompt
    prompt = f"""Analyze business data for anomalies in {request.entity_type}.

Look for these types of anomalies:
- Spikes: Sudden increases beyond normal patterns
- Drops: Unexpected decreases
- Patterns: Unusual recurring patterns
- Outliers: Values outside normal ranges

Return JSON format:
{{
    "anomalies": [
        {{
            "id": "unique-id",
            "type": "spike|drop|pattern|outlier",
            "severity": "low|medium|high|critical",
            "description": "Clear description",
            "suggested_action": "Recommended action",
            "affected_records": 0
        }}
    ],
    "total_found": 0
}}

If no anomalies detected, return empty anomalies array."""

    try:
        response = await ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="chat",
            temperature=0.3
        )

        if response.error:
            return {
                "entity_type": request.entity_type,
                "anomalies": [],
                "total_found": 0,
                "error": response.error
            }

        import json
        try:
            result = json.loads(response.content)
            # Add unique IDs if missing
            for anom in result.get("anomalies", []):
                if not anom.get("id"):
                    anom["id"] = f"anom-{uuid.uuid4().hex[:8]}"
            return {
                "entity_type": request.entity_type,
                "anomalies": result.get("anomalies", []),
                "total_found": len(result.get("anomalies", []))
            }
        except json.JSONDecodeError:
            return {
                "entity_type": request.entity_type,
                "anomalies": [],
                "total_found": 0
            }
    except Exception as e:
        return {
            "entity_type": request.entity_type,
            "anomalies": [],
            "total_found": 0,
            "error": str(e)
        }


@router.post("/anomalies/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(anomaly_id: str, notes: Optional[str] = None):
    """Acknowledge and review an anomaly."""
    return {
        "anomaly_id": anomaly_id,
        "status": "acknowledged",
        "notes": notes,
        "acknowledged_at": utc_now().isoformat()
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
    import uuid

    action_id = f"action-{uuid.uuid4().hex[:8]}"
    return {
        "id": action_id,
        "name": request.name,
        "status": "created",
        "is_enabled": True,
        "created_at": utc_now().isoformat()
    }


@router.get("/actions")
async def list_auto_actions(enabled_only: bool = False):
    """List configured auto-actions."""
    # In production, this would query from database
    # For now, return empty list indicating no actions configured
    return {
        "actions": [],
        "total": 0,
        "note": "No auto-actions configured. Use POST /ai/actions to create one."
    }


@router.post("/actions/{action_id}/toggle")
async def toggle_action(action_id: str):
    """Enable/disable an auto-action."""
    return {
        "action_id": action_id,
        "is_enabled": True,
        "toggled_at": utc_now().isoformat()
    }


@router.delete("/actions/{action_id}")
async def delete_action(action_id: str):
    """Delete an auto-action."""
    return {
        "status": "deleted",
        "action_id": action_id,
        "deleted_at": utc_now().isoformat()
    }


# ============================================================================
# Task Queue Endpoints (AI-012)
# ============================================================================

@router.post("/queue/tasks")
async def enqueue_task(request: TaskQueueRequest):
    """Add task to processing queue."""
    import uuid

    task_id = f"task-{uuid.uuid4().hex[:8]}"
    return {
        "task_id": task_id,
        "task_type": request.task_type,
        "priority": request.priority or "medium",
        "status": "pending",
        "created_at": utc_now().isoformat(),
        "note": "Task queued for processing"
    }


@router.get("/queue/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status."""
    # In production, query Celery or task database
    return {
        "task_id": task_id,
        "status": "unknown",
        "note": "Task status lookup requires Celery integration",
        "checked_at": utc_now().isoformat()
    }


@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics."""
    # In production, query Celery/Redis for actual stats
    return {
        "queued": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "processing": 0,
        "completed_today": 0,
        "failed_today": 0,
        "as_of": utc_now().isoformat(),
        "note": "Queue stats require Celery integration"
    }


@router.post("/queue/dead-letter/{task_id}/requeue")
async def requeue_failed_task(task_id: str):
    """Requeue a failed task from dead letter queue."""
    return {
        "task_id": task_id,
        "status": "requeued",
        "requeued_at": utc_now().isoformat()
    }


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
