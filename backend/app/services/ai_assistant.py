"""
AI ERP Assistant Services - Phase 20
Business logic for natural language queries, actions, and insights
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import re

from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_assistant import (
    AIConversation, AIMessage, AIAction, AIInsight, DailyBriefing,
    QueryIntent, QueryModule, ActionStatus, InsightType, InsightPriority,
)
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveStatus
from app.models.customer import Invoice, InvoiceStatus
from app.models.vendor import VendorBill, BillStatus
from app.models.bank import BankAccount
from app.models.crm import Lead, LeadStage
from app.schemas.ai_assistant import (
    AIQueryRequest, ParsedQuery, QueryResult, AIQueryResponse,
    AIActionCreate, AIActionResponse, AIActionConfirm,
    ConversationResponse, MessageResponse, ConversationListResponse,
    InsightResponse, DailyBriefingResponse, KeyMetric, PendingAction,
    SAMPLE_QUERIES,
)


class QueryParserService:
    """Service for parsing natural language queries"""

    # Intent patterns
    INTENT_PATTERNS = {
        QueryIntent.REPORT: [
            r'\b(show|generate|create|get|display)\b.*\b(report|statement|balance sheet|p&l|profit|loss)\b',
            r'\b(trial balance|income statement|cash flow)\b',
        ],
        QueryIntent.LOOKUP: [
            r'\b(show|get|display|find|what is|what\'s|list)\b',
            r'\b(how many|how much|what are)\b',
        ],
        QueryIntent.COMPARE: [
            r'\b(compare|vs|versus|against|difference)\b',
            r'\b(this month|last month|this year|last year|vs)\b.*\b(compare|than)\b',
        ],
        QueryIntent.TREND: [
            r'\b(trend|trending|growth|decline|pattern)\b',
            r'\b(over time|history|historical)\b',
        ],
        QueryIntent.FORECAST: [
            r'\b(forecast|predict|projection|expected|estimate)\b',
            r'\b(next month|next quarter|upcoming)\b',
        ],
        QueryIntent.CREATE: [
            r'\b(create|add|new|make)\b',
        ],
        QueryIntent.APPROVE: [
            r'\b(approve|accept|confirm)\b',
        ],
        QueryIntent.HELP: [
            r'\b(help|how to|how do|guide|explain how)\b',
        ],
    }

    # Module patterns
    MODULE_PATTERNS = {
        QueryModule.EMPLOYEE: [
            r'\b(employee|staff|team|workforce|headcount)\b',
        ],
        QueryModule.LEAVE: [
            r'\b(leave|vacation|sick|annual leave|time off|absence)\b',
        ],
        QueryModule.TIMESHEET: [
            r'\b(timesheet|hours|time entry|logged hours)\b',
        ],
        QueryModule.PAYROLL: [
            r'\b(payroll|salary|salaries|payslip|compensation|pf|esi)\b',
        ],
        QueryModule.CUSTOMER: [
            r'\b(customer|client)\b',
        ],
        QueryModule.INVOICE: [
            r'\b(invoice|receivable|ar|revenue|sales)\b',
        ],
        QueryModule.VENDOR: [
            r'\b(vendor|supplier)\b',
        ],
        QueryModule.BILL: [
            r'\b(bill|payable|ap|expense)\b',
        ],
        QueryModule.BANK: [
            r'\b(bank|cash|balance|account)\b',
        ],
        QueryModule.ACCOUNTING: [
            r'\b(accounting|journal|ledger|trial balance|balance sheet|p&l)\b',
        ],
        QueryModule.GST: [
            r'\b(gst|gstr|tax|itc|input tax)\b',
        ],
        QueryModule.TDS: [
            r'\b(tds|26q|challan|deduction)\b',
        ],
        QueryModule.CRM: [
            r'\b(lead|pipeline|crm|sales|opportunity|prospect)\b',
        ],
        QueryModule.PROJECT: [
            r'\b(project|task|milestone|deadline)\b',
        ],
    }

    # Entity patterns
    ENTITY_PATTERNS = {
        'date': r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
        'month': r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b',
        'period': r'\b(this month|last month|this quarter|last quarter|this year|last year|today|yesterday|this week|last week)\b',
        'amount': r'\b(?:rs\.?|inr|₹)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',
        'name': r'"([^"]+)"',
        'number': r'\b(\d+)\b',
    }

    def parse(self, query: str) -> ParsedQuery:
        """Parse natural language query"""
        query_lower = query.lower()

        # Detect intent
        intent, intent_confidence = self._detect_intent(query_lower)

        # Detect module
        module, module_confidence = self._detect_module(query_lower)

        # Extract entities
        entities = self._extract_entities(query)

        # Calculate overall confidence
        confidence = (intent_confidence + module_confidence) // 2

        return ParsedQuery(
            original_query=query,
            intent=intent,
            module=module,
            entities=entities,
            confidence=confidence
        )

    def _detect_intent(self, query: str) -> Tuple[QueryIntent, int]:
        """Detect query intent"""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent, 80

        return QueryIntent.LOOKUP, 50  # Default to lookup

    def _detect_module(self, query: str) -> Tuple[QueryModule, int]:
        """Detect relevant module"""
        for module, patterns in self.MODULE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return module, 85

        return QueryModule.GENERAL, 40

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query"""
        entities = {}

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0] if len(matches) == 1 else matches

        # Parse period entities
        if 'period' in entities:
            period = entities['period'].lower() if isinstance(entities['period'], str) else entities['period'][0].lower()
            entities['date_range'] = self._parse_period(period)

        return entities

    def _parse_period(self, period: str) -> Dict[str, date]:
        """Parse period string to date range"""
        today = date.today()

        if period == 'today':
            return {'from': today, 'to': today}
        elif period == 'yesterday':
            yesterday = today - timedelta(days=1)
            return {'from': yesterday, 'to': yesterday}
        elif period == 'this week':
            start = today - timedelta(days=today.weekday())
            return {'from': start, 'to': today}
        elif period == 'last week':
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            return {'from': start, 'to': end}
        elif period == 'this month':
            start = today.replace(day=1)
            return {'from': start, 'to': today}
        elif period == 'last month':
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return {'from': last_month_start, 'to': last_month_end}
        elif period == 'this quarter':
            quarter_start = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
            return {'from': quarter_start, 'to': today}
        elif period == 'this year':
            return {'from': date(today.year, 1, 1), 'to': today}
        elif period == 'last year':
            return {'from': date(today.year - 1, 1, 1), 'to': date(today.year - 1, 12, 31)}

        return {'from': today, 'to': today}


class QueryExecutorService:
    """Service for executing parsed queries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, parsed: ParsedQuery, user_id: UUID) -> QueryResult:
        """Execute a parsed query"""
        try:
            # Route to appropriate handler
            handler = self._get_handler(parsed.module, parsed.intent)
            if handler:
                data = await handler(parsed)
                return QueryResult(
                    success=True,
                    data=data,
                    message=self._format_response(parsed, data),
                    visualization_type=self._get_visualization_type(parsed)
                )
            else:
                return QueryResult(
                    success=True,
                    data=None,
                    message=f"I understand you're asking about {parsed.module.value}. Let me help you with that."
                )
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                message=f"I encountered an error processing your request: {str(e)}"
            )

    def _get_handler(self, module: QueryModule, intent: QueryIntent):
        """Get appropriate handler for module/intent"""
        handlers = {
            (QueryModule.EMPLOYEE, QueryIntent.LOOKUP): self._handle_employee_lookup,
            (QueryModule.LEAVE, QueryIntent.LOOKUP): self._handle_leave_lookup,
            (QueryModule.INVOICE, QueryIntent.LOOKUP): self._handle_invoice_lookup,
            (QueryModule.BANK, QueryIntent.LOOKUP): self._handle_bank_lookup,
            (QueryModule.CRM, QueryIntent.LOOKUP): self._handle_crm_lookup,
        }
        return handlers.get((module, intent))

    async def _handle_employee_lookup(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Handle employee lookup queries"""
        query = parsed.original_query.lower()

        if 'how many' in query or 'count' in query:
            result = await self.db.execute(
                select(func.count()).select_from(Employee)
            )
            count = result.scalar()
            return {'count': count, 'type': 'employee_count'}

        elif 'on leave' in query or 'leave today' in query:
            today = date.today()
            result = await self.db.execute(
                select(Employee)
                .join(LeaveApplication)
                .where(
                    LeaveApplication.status == LeaveStatus.APPROVED,
                    LeaveApplication.start_date <= today,
                    LeaveApplication.end_date >= today
                )
            )
            employees = result.scalars().all()
            return {
                'employees': [{'name': f"{e.first_name} {e.last_name}", 'id': str(e.id)} for e in employees],
                'count': len(employees),
                'type': 'employees_on_leave'
            }

        return {'message': 'Employee data retrieved', 'type': 'general'}

    async def _handle_leave_lookup(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Handle leave lookup queries"""
        query = parsed.original_query.lower()

        if 'pending' in query:
            result = await self.db.execute(
                select(func.count())
                .select_from(LeaveApplication)
                .where(LeaveApplication.status == LeaveStatus.PENDING)
            )
            count = result.scalar()
            return {'pending_count': count, 'type': 'pending_leaves'}

        return {'message': 'Leave data retrieved', 'type': 'general'}

    async def _handle_invoice_lookup(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Handle invoice lookup queries"""
        query = parsed.original_query.lower()

        if 'overdue' in query:
            today = date.today()
            result = await self.db.execute(
                select(func.count(), func.sum(Invoice.balance_due))
                .where(
                    Invoice.due_date < today,
                    Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID])
                )
            )
            row = result.one()
            return {
                'overdue_count': row[0] or 0,
                'overdue_amount': float(row[1] or 0),
                'type': 'overdue_invoices'
            }

        elif 'revenue' in query or 'total' in query:
            # Get date range from entities
            date_range = parsed.entities.get('date_range', {})
            from_date = date_range.get('from', date.today().replace(day=1))
            to_date = date_range.get('to', date.today())

            result = await self.db.execute(
                select(func.sum(Invoice.total_amount))
                .where(
                    Invoice.invoice_date >= from_date,
                    Invoice.invoice_date <= to_date,
                    Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
                )
            )
            total = result.scalar() or Decimal("0")
            return {
                'total_revenue': float(total),
                'period': f"{from_date} to {to_date}",
                'type': 'revenue_total'
            }

        return {'message': 'Invoice data retrieved', 'type': 'general'}

    async def _handle_bank_lookup(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Handle bank/cash lookup queries"""
        query = parsed.original_query.lower()

        if 'balance' in query or 'cash' in query:
            result = await self.db.execute(
                select(func.sum(BankAccount.current_balance))
                .where(BankAccount.is_active == True)
            )
            balance = result.scalar() or Decimal("0")
            return {
                'total_balance': float(balance),
                'type': 'cash_balance'
            }

        return {'message': 'Bank data retrieved', 'type': 'general'}

    async def _handle_crm_lookup(self, parsed: ParsedQuery) -> Dict[str, Any]:
        """Handle CRM lookup queries"""
        query = parsed.original_query.lower()

        if 'pipeline' in query:
            result = await self.db.execute(
                select(Lead.stage, func.count(), func.sum(Lead.estimated_value))
                .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
                .group_by(Lead.stage)
            )
            stages = result.all()
            return {
                'pipeline': [
                    {'stage': s.value, 'count': c, 'value': float(v or 0)}
                    for s, c, v in stages
                ],
                'type': 'pipeline_summary'
            }

        elif 'follow-up' in query or 'followup' in query:
            today = date.today()
            result = await self.db.execute(
                select(func.count())
                .select_from(Lead)
                .where(
                    Lead.next_followup_date <= today,
                    Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
                )
            )
            count = result.scalar() or 0
            return {
                'overdue_followups': count,
                'type': 'followup_count'
            }

        return {'message': 'CRM data retrieved', 'type': 'general'}

    def _format_response(self, parsed: ParsedQuery, data: Dict[str, Any]) -> str:
        """Format response message"""
        data_type = data.get('type', 'general')

        responses = {
            'employee_count': f"We currently have {data.get('count', 0)} employees.",
            'employees_on_leave': f"There are {data.get('count', 0)} employees on leave today.",
            'pending_leaves': f"There are {data.get('pending_count', 0)} pending leave requests.",
            'overdue_invoices': f"There are {data.get('overdue_count', 0)} overdue invoices totaling ₹{data.get('overdue_amount', 0):,.2f}.",
            'revenue_total': f"Total revenue for {data.get('period', 'the period')}: ₹{data.get('total_revenue', 0):,.2f}",
            'cash_balance': f"Current cash balance across all accounts: ₹{data.get('total_balance', 0):,.2f}",
            'pipeline_summary': f"Your pipeline has {sum(s['count'] for s in data.get('pipeline', []))} active leads.",
            'followup_count': f"You have {data.get('overdue_followups', 0)} leads needing follow-up.",
        }

        return responses.get(data_type, "Here's the information you requested.")

    def _get_visualization_type(self, parsed: ParsedQuery) -> str:
        """Determine appropriate visualization"""
        if parsed.intent == QueryIntent.TREND:
            return "chart"
        elif parsed.intent == QueryIntent.COMPARE:
            return "comparison"
        elif parsed.intent == QueryIntent.REPORT:
            return "table"
        return "card"


class ConversationService:
    """Service for managing AI conversations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = QueryParserService()
        self.executor = QueryExecutorService(db)

    async def process_query(
        self,
        request: AIQueryRequest,
        user_id: UUID
    ) -> AIQueryResponse:
        """Process a natural language query"""
        # Get or create conversation
        if request.conversation_id:
            conversation = await self._get_conversation(request.conversation_id)
        else:
            conversation = await self._create_conversation(user_id, request.context)

        # Parse query
        parsed = self.parser.parse(request.query)

        # Create user message
        user_message = AIMessage(
            conversation_id=conversation.id,
            role="user",
            content=request.query,
            intent=parsed.intent,
            module=parsed.module,
            entities=parsed.entities,
            confidence=parsed.confidence
        )
        self.db.add(user_message)

        # Execute query
        result = await self.executor.execute(parsed, user_id)

        # Create assistant response
        assistant_message = AIMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=result.message,
            data_returned={'success': result.success, 'data_summary': str(result.data)[:500] if result.data else None}
        )
        self.db.add(assistant_message)

        # Update conversation
        conversation.last_activity_at = datetime.utcnow()
        if not conversation.title and request.query:
            conversation.title = request.query[:100]

        await self.db.commit()
        await self.db.refresh(user_message)
        await self.db.refresh(assistant_message)

        # Get suggested follow-up queries
        suggested = self._get_suggested_queries(parsed.module)

        return AIQueryResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            response=result.message,
            parsed_query=parsed,
            result=result,
            suggested_queries=suggested,
            action_required=False
        )

    async def _get_conversation(self, conversation_id: UUID) -> AIConversation:
        """Get conversation by ID"""
        query = select(AIConversation).where(AIConversation.id == conversation_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _create_conversation(
        self,
        user_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> AIConversation:
        """Create new conversation"""
        conversation = AIConversation(
            user_id=user_id,
            context_data=context
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def list_conversations(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[ConversationListResponse]:
        """List user conversations"""
        query = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.last_activity_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        conversations = result.scalars().all()

        responses = []
        for conv in conversations:
            # Count messages
            count_query = (
                select(func.count())
                .select_from(AIMessage)
                .where(AIMessage.conversation_id == conv.id)
            )
            count_result = await self.db.execute(count_query)
            message_count = count_result.scalar()

            responses.append(ConversationListResponse(
                id=conv.id,
                title=conv.title,
                started_at=conv.started_at,
                last_activity_at=conv.last_activity_at,
                message_count=message_count
            ))

        return responses

    async def get_conversation_with_messages(
        self,
        conversation_id: UUID
    ) -> Optional[ConversationResponse]:
        """Get conversation with messages"""
        query = (
            select(AIConversation)
            .options(selectinload(AIConversation.messages))
            .where(AIConversation.id == conversation_id)
        )
        result = await self.db.execute(query)
        conv = result.scalar_one_or_none()

        if not conv:
            return None

        return ConversationResponse(
            id=conv.id,
            title=conv.title,
            context_module=conv.context_module,
            started_at=conv.started_at,
            last_activity_at=conv.last_activity_at,
            is_active=conv.is_active,
            messages=[
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    intent=m.intent,
                    module=m.module,
                    created_at=m.created_at
                )
                for m in conv.messages
            ]
        )

    def _get_suggested_queries(self, module: QueryModule) -> List[str]:
        """Get suggested queries for module"""
        return SAMPLE_QUERIES.get(module, SAMPLE_QUERIES[QueryModule.GENERAL])[:3]


class InsightService:
    """Service for AI insights"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_insights(
        self,
        user_id: UUID,
        roles: List[str]
    ) -> List[InsightResponse]:
        """Get active insights for user"""
        now = datetime.utcnow()

        query = (
            select(AIInsight)
            .where(
                AIInsight.is_dismissed == False,
                or_(
                    AIInsight.valid_until.is_(None),
                    AIInsight.valid_until > now
                )
            )
            .order_by(AIInsight.priority.desc(), AIInsight.created_at.desc())
            .limit(10)
        )

        result = await self.db.execute(query)
        insights = result.scalars().all()

        return [
            InsightResponse(
                id=i.id,
                insight_type=i.insight_type,
                priority=i.priority,
                module=i.module,
                title=i.title,
                summary=i.summary,
                details=i.details,
                recommendations=i.recommendations,
                suggested_action=i.suggested_action,
                action_url=i.action_url,
                valid_until=i.valid_until,
                created_at=i.created_at
            )
            for i in insights
        ]

    async def dismiss_insight(self, insight_id: UUID, user_id: UUID):
        """Dismiss an insight"""
        query = select(AIInsight).where(AIInsight.id == insight_id)
        result = await self.db.execute(query)
        insight = result.scalar_one_or_none()

        if insight:
            insight.is_dismissed = True
            insight.dismissed_by = user_id
            insight.dismissed_at = datetime.utcnow()
            await self.db.commit()

    async def generate_insights(self):
        """Generate proactive insights (scheduled job)"""
        insights = []
        today = date.today()

        # Check overdue invoices
        overdue_query = (
            select(func.count(), func.sum(Invoice.balance_due))
            .where(
                Invoice.due_date < today,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID])
            )
        )
        result = await self.db.execute(overdue_query)
        overdue_count, overdue_amount = result.one()

        if overdue_count and overdue_count > 0:
            insight = AIInsight(
                insight_type=InsightType.ALERT,
                priority=InsightPriority.HIGH if overdue_amount > 100000 else InsightPriority.MEDIUM,
                module=QueryModule.INVOICE,
                title="Overdue Invoices Require Attention",
                summary=f"You have {overdue_count} overdue invoices totaling ₹{float(overdue_amount or 0):,.2f}",
                recommendations=["Review overdue invoices", "Send payment reminders", "Consider escalation for old dues"],
                suggested_action="view_overdue_invoices",
                action_url="/ar/invoices?status=overdue"
            )
            self.db.add(insight)
            insights.append(insight)

        # Check pending leave approvals
        pending_leave_query = (
            select(func.count())
            .select_from(LeaveApplication)
            .where(LeaveApplication.status == LeaveStatus.PENDING)
        )
        result = await self.db.execute(pending_leave_query)
        pending_count = result.scalar()

        if pending_count and pending_count > 0:
            insight = AIInsight(
                insight_type=InsightType.REMINDER,
                priority=InsightPriority.MEDIUM,
                module=QueryModule.LEAVE,
                title="Pending Leave Requests",
                summary=f"There are {pending_count} leave requests waiting for approval",
                recommendations=["Review pending requests", "Communicate with team about coverage"],
                suggested_action="approve_leave",
                action_url="/leave/pending"
            )
            self.db.add(insight)
            insights.append(insight)

        # Check leads needing follow-up
        followup_query = (
            select(func.count())
            .select_from(Lead)
            .where(
                Lead.next_followup_date <= today,
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
        )
        result = await self.db.execute(followup_query)
        followup_count = result.scalar()

        if followup_count and followup_count > 0:
            insight = AIInsight(
                insight_type=InsightType.REMINDER,
                priority=InsightPriority.MEDIUM,
                module=QueryModule.CRM,
                title="Leads Need Follow-up",
                summary=f"{followup_count} leads have overdue follow-up dates",
                recommendations=["Contact leads", "Update lead status", "Schedule next actions"],
                suggested_action="view_leads",
                action_url="/crm?followup=overdue"
            )
            self.db.add(insight)
            insights.append(insight)

        await self.db.commit()
        return insights


class DailyBriefingService:
    """Service for daily AI briefings"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_generate_briefing(
        self,
        user_id: UUID,
        briefing_date: date
    ) -> DailyBriefingResponse:
        """Get or generate daily briefing"""
        # Check if briefing exists
        query = (
            select(DailyBriefing)
            .where(
                DailyBriefing.user_id == user_id,
                DailyBriefing.briefing_date == briefing_date
            )
        )
        result = await self.db.execute(query)
        briefing = result.scalar_one_or_none()

        if not briefing:
            briefing = await self._generate_briefing(user_id, briefing_date)

        return await self._to_response(briefing)

    async def _generate_briefing(
        self,
        user_id: UUID,
        briefing_date: date
    ) -> DailyBriefing:
        """Generate daily briefing"""
        # Gather key metrics
        key_metrics = await self._gather_metrics()

        # Gather pending actions
        pending_actions = await self._gather_pending_actions()

        # Create summary
        summary = self._create_summary(key_metrics, pending_actions)

        briefing = DailyBriefing(
            user_id=user_id,
            briefing_date=briefing_date,
            summary=summary,
            key_metrics=[m.model_dump() for m in key_metrics],
            pending_actions=[p.model_dump() for p in pending_actions],
            insights=[]
        )

        self.db.add(briefing)
        await self.db.commit()
        await self.db.refresh(briefing)

        return briefing

    async def _gather_metrics(self) -> List[KeyMetric]:
        """Gather key metrics for briefing"""
        metrics = []
        today = date.today()
        month_start = today.replace(day=1)

        # Revenue this month
        revenue_query = (
            select(func.sum(Invoice.total_amount))
            .where(
                Invoice.invoice_date >= month_start,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
        )
        result = await self.db.execute(revenue_query)
        revenue = result.scalar() or Decimal("0")
        metrics.append(KeyMetric(
            name="Revenue (MTD)",
            value=f"₹{float(revenue):,.0f}",
            change=None,
            change_type=None
        ))

        # Cash balance
        cash_query = (
            select(func.sum(BankAccount.current_balance))
            .where(BankAccount.is_active == True)
        )
        result = await self.db.execute(cash_query)
        cash = result.scalar() or Decimal("0")
        metrics.append(KeyMetric(
            name="Cash Balance",
            value=f"₹{float(cash):,.0f}",
            change=None,
            change_type=None
        ))

        # Pipeline value
        pipeline_query = (
            select(func.sum(Lead.estimated_value))
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
        )
        result = await self.db.execute(pipeline_query)
        pipeline = result.scalar() or Decimal("0")
        metrics.append(KeyMetric(
            name="Pipeline Value",
            value=f"₹{float(pipeline):,.0f}",
            change=None,
            change_type=None
        ))

        return metrics

    async def _gather_pending_actions(self) -> List[PendingAction]:
        """Gather pending actions"""
        actions = []

        # Pending leave approvals
        leave_query = (
            select(func.count())
            .select_from(LeaveApplication)
            .where(LeaveApplication.status == LeaveStatus.PENDING)
        )
        result = await self.db.execute(leave_query)
        pending_leaves = result.scalar() or 0
        if pending_leaves > 0:
            actions.append(PendingAction(
                type="leave_approval",
                description="Leave requests pending approval",
                count=pending_leaves,
                priority="medium",
                action_url="/leave/pending"
            ))

        # Overdue invoices
        today = date.today()
        overdue_query = (
            select(func.count())
            .select_from(Invoice)
            .where(
                Invoice.due_date < today,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID])
            )
        )
        result = await self.db.execute(overdue_query)
        overdue = result.scalar() or 0
        if overdue > 0:
            actions.append(PendingAction(
                type="overdue_invoices",
                description="Invoices past due date",
                count=overdue,
                priority="high",
                action_url="/ar/invoices?status=overdue"
            ))

        # Lead follow-ups
        followup_query = (
            select(func.count())
            .select_from(Lead)
            .where(
                Lead.next_followup_date <= today,
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
        )
        result = await self.db.execute(followup_query)
        followups = result.scalar() or 0
        if followups > 0:
            actions.append(PendingAction(
                type="lead_followup",
                description="Leads needing follow-up",
                count=followups,
                priority="medium",
                action_url="/crm?followup=overdue"
            ))

        return actions

    def _create_summary(
        self,
        metrics: List[KeyMetric],
        actions: List[PendingAction]
    ) -> str:
        """Create summary text"""
        parts = ["Good morning! Here's your daily briefing."]

        if metrics:
            parts.append(f"Key metrics: {', '.join(f'{m.name}: {m.value}' for m in metrics[:3])}")

        if actions:
            total_actions = sum(a.count for a in actions)
            parts.append(f"You have {total_actions} items requiring attention.")

        return " ".join(parts)

    async def _to_response(self, briefing: DailyBriefing) -> DailyBriefingResponse:
        """Convert to response schema"""
        return DailyBriefingResponse(
            id=briefing.id,
            briefing_date=briefing.briefing_date,
            summary=briefing.summary,
            key_metrics=[KeyMetric(**m) for m in (briefing.key_metrics or [])],
            pending_actions=[PendingAction(**p) for p in (briefing.pending_actions or [])],
            insights=[],
            is_read=briefing.is_read,
            generated_at=briefing.generated_at
        )

    async def mark_read(self, briefing_id: UUID):
        """Mark briefing as read"""
        query = select(DailyBriefing).where(DailyBriefing.id == briefing_id)
        result = await self.db.execute(query)
        briefing = result.scalar_one_or_none()

        if briefing:
            briefing.is_read = True
            briefing.read_at = datetime.utcnow()
            await self.db.commit()
