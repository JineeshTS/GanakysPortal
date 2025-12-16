"""
AI Service layer with Claude API integration.
WBS Reference: Phase 10 - AI Core Infrastructure
"""
import json
import time
import base64
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import asyncio
import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import (
    AIRequest,
    AIFeedback,
    AIPromptTemplate,
    DocumentExtractionResult,
    AIRequestType,
    AIModel,
)
from app.models.edms import Document
from app.core.config import settings

logger = logging.getLogger(__name__)


# Cost per 1M tokens (approximate USD)
MODEL_COSTS = {
    AIModel.CLAUDE_SONNET: {"input": 3.0, "output": 15.0},
    AIModel.CLAUDE_HAIKU: {"input": 0.25, "output": 1.25},
}


class AIService:
    """Service for AI operations using Claude API."""

    def __init__(self):
        """Initialize AI service."""
        self._client = None

    @property
    def client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
                if api_key:
                    self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                logger.warning("anthropic package not installed")
        return self._client

    @staticmethod
    def calculate_cost(model: AIModel, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate estimated cost for token usage."""
        costs = MODEL_COSTS.get(model, MODEL_COSTS[AIModel.CLAUDE_SONNET])
        input_cost = Decimal(str(input_tokens)) / 1000000 * Decimal(str(costs["input"]))
        output_cost = Decimal(str(output_tokens)) / 1000000 * Decimal(str(costs["output"]))
        return input_cost + output_cost

    async def _make_request(
        self,
        db: AsyncSession,
        user_id: UUID,
        request_type: AIRequestType,
        system_prompt: str,
        user_prompt: str,
        model: AIModel = AIModel.CLAUDE_SONNET,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        images: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[str, AIRequest]:
        """Make a request to Claude API with logging."""
        start_time = time.time()

        # Create AI request log entry
        ai_request = AIRequest(
            user_id=user_id,
            request_type=request_type,
            model=model,
            entity_type=entity_type,
            entity_id=entity_id,
            prompt_summary=user_prompt[:500] if user_prompt else None,
        )
        db.add(ai_request)
        await db.flush()

        try:
            if not self.client:
                raise ValueError("Claude API client not configured. Please set ANTHROPIC_API_KEY.")

            # Build messages
            messages = []
            content = []

            # Add images if provided
            if images:
                for img in images:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img.get("media_type", "image/png"),
                            "data": img["data"],
                        }
                    })

            # Add text content
            content.append({"type": "text", "text": user_prompt})

            messages.append({"role": "user", "content": content})

            # Make API call
            response = self.client.messages.create(
                model=model.value,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
            )

            # Extract response
            response_text = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Update request log
            latency_ms = int((time.time() - start_time) * 1000)
            ai_request.input_tokens = input_tokens
            ai_request.output_tokens = output_tokens
            ai_request.total_tokens = input_tokens + output_tokens
            ai_request.estimated_cost = self.calculate_cost(model, input_tokens, output_tokens)
            ai_request.latency_ms = latency_ms
            ai_request.response_summary = response_text[:500] if response_text else None
            ai_request.success = True

            return response_text, ai_request

        except Exception as e:
            logger.error(f"AI request failed: {e}")
            ai_request.success = False
            ai_request.error_message = str(e)
            ai_request.latency_ms = int((time.time() - start_time) * 1000)
            raise

    # Document Classification

    async def classify_document(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        image_data: str,
        media_type: str = "image/png",
    ) -> Dict[str, Any]:
        """Classify document type using Claude Vision."""
        system_prompt = """You are a document classification expert. Analyze the provided document image and classify it into one of the following categories:

- invoice: Sales invoice, tax invoice, proforma invoice
- bill: Vendor bill, expense bill, utility bill
- receipt: Payment receipt, cash memo, purchase receipt
- bank_statement: Bank account statement
- salary_slip: Payslip, salary statement
- tax_document: Form 16, TDS certificate, IT return
- identity: Aadhaar, PAN, passport, driving license
- contract: Agreement, MOU, employment contract
- other: Any other document type

Respond in JSON format:
{
    "document_type": "category",
    "confidence": 0.95,
    "subtypes": ["specific type if applicable"],
    "reasoning": "brief explanation"
}"""

        user_prompt = "Classify this document and provide your analysis."

        response_text, ai_request = await self._make_request(
            db=db,
            user_id=user_id,
            request_type=AIRequestType.DOCUMENT_CLASSIFICATION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=AIModel.CLAUDE_SONNET,
            entity_type="document",
            entity_id=document_id,
            images=[{"data": image_data, "media_type": media_type}],
        )

        # Parse response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"document_type": "other", "confidence": 0.5, "raw_response": response_text}

        result["ai_request_id"] = str(ai_request.id)
        return result

    # Invoice/Bill Extraction

    async def extract_invoice(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        image_data: str,
        media_type: str = "image/png",
    ) -> Dict[str, Any]:
        """Extract data from invoice/bill using Claude Vision."""
        system_prompt = """You are an expert at extracting data from Indian invoices and bills. Extract all relevant information from the provided document image.

Return a JSON object with the following structure:
{
    "vendor_name": "Company/vendor name",
    "vendor_gstin": "GSTIN if present (15 chars)",
    "vendor_address": "Full address",
    "invoice_number": "Invoice/bill number",
    "invoice_date": "Date in YYYY-MM-DD format",
    "due_date": "Due date if present",
    "subtotal": 0.00,
    "cgst": 0.00,
    "sgst": 0.00,
    "igst": 0.00,
    "tax_amount": 0.00,
    "total_amount": 0.00,
    "currency": "INR",
    "line_items": [
        {
            "description": "Item description",
            "hsn_sac": "HSN/SAC code",
            "quantity": 1,
            "unit_price": 0.00,
            "tax_rate": 18,
            "amount": 0.00
        }
    ],
    "payment_terms": "Net 30",
    "bank_details": {
        "bank_name": "Bank name",
        "account_number": "Account number",
        "ifsc_code": "IFSC code"
    },
    "confidence_scores": {
        "vendor_name": 0.95,
        "invoice_number": 0.98
    }
}

Extract as much information as possible. Use null for fields that cannot be determined."""

        user_prompt = "Extract all invoice/bill information from this document."

        response_text, ai_request = await self._make_request(
            db=db,
            user_id=user_id,
            request_type=AIRequestType.DOCUMENT_EXTRACTION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=AIModel.CLAUDE_SONNET,
            entity_type="document",
            entity_id=document_id,
            images=[{"data": image_data, "media_type": media_type}],
        )

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"error": "Failed to parse response", "raw_response": response_text}

        result["ai_request_id"] = str(ai_request.id)
        return result

    # Bank Statement Extraction

    async def extract_bank_statement(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        image_data: str,
        media_type: str = "image/png",
    ) -> Dict[str, Any]:
        """Extract data from bank statement using Claude Vision."""
        system_prompt = """You are an expert at extracting data from Indian bank statements. Extract all relevant information from the provided document image.

Return a JSON object with the following structure:
{
    "bank_name": "Bank name",
    "branch": "Branch name if visible",
    "account_number": "Account number (may be partially masked)",
    "account_holder": "Account holder name",
    "account_type": "savings/current",
    "statement_period": {
        "from": "YYYY-MM-DD",
        "to": "YYYY-MM-DD"
    },
    "opening_balance": 0.00,
    "closing_balance": 0.00,
    "currency": "INR",
    "transactions": [
        {
            "date": "YYYY-MM-DD",
            "description": "Transaction description",
            "reference": "Ref number/UTR",
            "debit": 0.00,
            "credit": 0.00,
            "balance": 0.00,
            "transaction_type": "NEFT/IMPS/UPI/ATM/etc"
        }
    ],
    "summary": {
        "total_credits": 0.00,
        "total_debits": 0.00,
        "transaction_count": 0
    }
}

Extract all transactions visible on the page. Use null for fields that cannot be determined."""

        user_prompt = "Extract all bank statement information from this document, including all transactions."

        response_text, ai_request = await self._make_request(
            db=db,
            user_id=user_id,
            request_type=AIRequestType.DOCUMENT_EXTRACTION,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=AIModel.CLAUDE_SONNET,
            max_tokens=8192,  # More tokens for transaction lists
            entity_type="document",
            entity_id=document_id,
            images=[{"data": image_data, "media_type": media_type}],
        )

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"error": "Failed to parse response", "raw_response": response_text}

        result["ai_request_id"] = str(ai_request.id)
        return result

    # Natural Language Query

    async def process_query(
        self,
        db: AsyncSession,
        user_id: UUID,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process natural language query about ERP data."""
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2, default=str)}"

        system_prompt = f"""You are an AI assistant for GanaPortal ERP system. You help users with questions about:
- Employee management and HR
- Payroll and salary information
- Leave and attendance
- Timesheets and project tracking
- Statutory compliance (PF, ESI, TDS)
- Document management

Provide helpful, accurate responses based on the user's query and any provided context.
If you cannot answer based on available information, say so clearly.
{context_str}"""

        user_prompt = query

        response_text, ai_request = await self._make_request(
            db=db,
            user_id=user_id,
            request_type=AIRequestType.QUERY,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=AIModel.CLAUDE_SONNET,
            temperature=0.3,
        )

        return {
            "response": response_text,
            "ai_request_id": str(ai_request.id),
            "tokens_used": ai_request.total_tokens,
        }

    # Insight Generation

    async def generate_insights(
        self,
        db: AsyncSession,
        user_id: UUID,
        insight_type: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate insights from ERP data."""
        system_prompt = """You are a business analyst AI for GanaPortal ERP. Generate actionable insights from the provided data.

Return insights in this JSON format:
{
    "insights": [
        {
            "title": "Insight title",
            "description": "Detailed description",
            "value": "Key metric or value",
            "trend": "up/down/stable",
            "change_percentage": 10.5,
            "severity": "info/warning/critical",
            "recommendations": ["Action 1", "Action 2"]
        }
    ],
    "summary": "Executive summary of findings",
    "key_metrics": {
        "metric_name": value
    }
}"""

        user_prompt = f"""Generate insights for {insight_type}.

Data:
{json.dumps(data, indent=2, default=str)}

Analyze the data and provide meaningful business insights."""

        response_text, ai_request = await self._make_request(
            db=db,
            user_id=user_id,
            request_type=AIRequestType.INSIGHT,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=AIModel.CLAUDE_SONNET,
            temperature=0.2,
        )

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            result = {"summary": response_text, "insights": []}

        result["ai_request_id"] = str(ai_request.id)
        result["generated_at"] = datetime.utcnow().isoformat()
        return result

    # Feedback Operations

    @staticmethod
    async def submit_feedback(
        db: AsyncSession,
        user_id: UUID,
        ai_request_id: UUID,
        feedback_type: str,
        rating: Optional[int] = None,
        original_value: Optional[str] = None,
        corrected_value: Optional[str] = None,
        field_name: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> AIFeedback:
        """Submit feedback for an AI request."""
        feedback = AIFeedback(
            ai_request_id=ai_request_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            original_value=original_value,
            corrected_value=corrected_value,
            field_name=field_name,
            comment=comment,
        )
        db.add(feedback)
        await db.flush()
        return feedback

    # Document Processing with Extraction Storage

    async def process_document(
        self,
        db: AsyncSession,
        user_id: UUID,
        document_id: UUID,
        image_data: str,
        media_type: str = "image/png",
        document_type_hint: Optional[str] = None,
    ) -> DocumentExtractionResult:
        """Process document: classify and extract data."""
        # First classify the document
        if document_type_hint:
            doc_type = document_type_hint
            confidence = 1.0
        else:
            classification = await self.classify_document(
                db, user_id, document_id, image_data, media_type
            )
            doc_type = classification.get("document_type", "other")
            confidence = classification.get("confidence", 0.5)

        # Extract based on document type
        if doc_type in ["invoice", "bill"]:
            extracted = await self.extract_invoice(
                db, user_id, document_id, image_data, media_type
            )
        elif doc_type == "bank_statement":
            extracted = await self.extract_bank_statement(
                db, user_id, document_id, image_data, media_type
            )
        else:
            # Generic extraction for other types
            extracted = {"document_type": doc_type, "raw_classification": doc_type}

        ai_request_id = UUID(extracted.pop("ai_request_id", str(UUID(int=0))))

        # Store extraction result
        result = DocumentExtractionResult(
            document_id=document_id,
            ai_request_id=ai_request_id,
            document_type=doc_type,
            confidence_score=Decimal(str(confidence)),
            extracted_data=extracted,
        )
        db.add(result)
        await db.flush()

        return result

    # Usage Statistics

    @staticmethod
    async def get_usage_stats(
        db: AsyncSession,
        user_id: Optional[UUID] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get AI usage statistics."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)

        query = select(AIRequest).where(AIRequest.created_at >= cutoff)
        if user_id:
            query = query.where(AIRequest.user_id == user_id)

        result = await db.execute(query)
        requests = result.scalars().all()

        if not requests:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": Decimal("0"),
                "requests_by_type": {},
                "average_latency_ms": 0,
                "success_rate": 0,
                "period": f"last_{days}_days",
            }

        total_requests = len(requests)
        total_tokens = sum(r.total_tokens for r in requests)
        total_cost = sum(r.estimated_cost for r in requests)
        successful = sum(1 for r in requests if r.success)
        total_latency = sum(r.latency_ms for r in requests)

        requests_by_type = {}
        for r in requests:
            req_type = r.request_type.value
            requests_by_type[req_type] = requests_by_type.get(req_type, 0) + 1

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "requests_by_type": requests_by_type,
            "average_latency_ms": total_latency / total_requests if total_requests else 0,
            "success_rate": successful / total_requests if total_requests else 0,
            "period": f"last_{days}_days",
        }

    # Prompt Template Operations

    @staticmethod
    async def get_prompt_template(
        db: AsyncSession, name: str
    ) -> Optional[AIPromptTemplate]:
        """Get active prompt template by name."""
        result = await db.execute(
            select(AIPromptTemplate).where(
                AIPromptTemplate.name == name,
                AIPromptTemplate.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_prompt_template(
        db: AsyncSession, **kwargs
    ) -> AIPromptTemplate:
        """Create new prompt template."""
        template = AIPromptTemplate(**kwargs)
        db.add(template)
        await db.flush()
        return template

    @staticmethod
    async def list_prompt_templates(
        db: AsyncSession,
        request_type: Optional[AIRequestType] = None,
        active_only: bool = True,
    ) -> List[AIPromptTemplate]:
        """List prompt templates."""
        query = select(AIPromptTemplate)
        if request_type:
            query = query.where(AIPromptTemplate.request_type == request_type)
        if active_only:
            query = query.where(AIPromptTemplate.is_active == True)
        query = query.order_by(AIPromptTemplate.name)

        result = await db.execute(query)
        return result.scalars().all()


# Create singleton instance
ai_service = AIService()
