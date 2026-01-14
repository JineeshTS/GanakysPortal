"""
AI-006: Chat Backend Service with Context Management
AI-powered conversational interface with session context
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Chat message."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Chat session with context."""
    id: str
    user_id: str
    company_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class ChatService:
    """
    AI Chat service with context management.

    Features:
    - Multi-turn conversations
    - Session management
    - Context injection from business data
    - Function calling for data retrieval
    - Response streaming
    """

    # Session timeout (30 minutes)
    SESSION_TIMEOUT = timedelta(minutes=30)

    # Maximum context window tokens
    MAX_CONTEXT_TOKENS = 8000

    # Available functions the AI can call
    AVAILABLE_FUNCTIONS = {
        "get_employee_info": {
            "description": "Get employee details by ID or name",
            "parameters": ["employee_id", "name"]
        },
        "get_leave_balance": {
            "description": "Get leave balance for an employee",
            "parameters": ["employee_id"]
        },
        "get_payroll_summary": {
            "description": "Get payroll summary for a period",
            "parameters": ["month", "year"]
        },
        "get_invoice_status": {
            "description": "Get invoice status and details",
            "parameters": ["invoice_number"]
        },
        "get_expense_report": {
            "description": "Get expense report for period",
            "parameters": ["start_date", "end_date"]
        },
        "get_attendance_report": {
            "description": "Get attendance report",
            "parameters": ["employee_id", "month"]
        },
    }

    def __init__(self, ai_service):
        """Initialize with core AI service."""
        self.ai_service = ai_service
        self._sessions: Dict[str, ChatSession] = {}

    async def create_session(
        self,
        user_id: str,
        company_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create new chat session."""
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            company_id=company_id,
            context=initial_context or {}
        )

        # Add system message with context
        system_message = self._build_system_message(session)
        session.messages.append(ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.SYSTEM,
            content=system_message,
            timestamp=datetime.utcnow()
        ))

        self._sessions[session.id] = session
        return session

    async def send_message(
        self,
        session_id: str,
        content: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> ChatMessage:
        """
        Send message and get AI response.

        Args:
            session_id: Chat session ID
            content: User message content
            attachments: Optional file attachments

        Returns:
            AI response message
        """
        session = self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Check session timeout
        if datetime.utcnow() - session.last_activity > self.SESSION_TIMEOUT:
            session.is_active = False
            raise ValueError("Session expired")

        # Add user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.utcnow(),
            metadata={"attachments": attachments} if attachments else {}
        )
        session.messages.append(user_message)

        # Prepare messages for AI
        ai_messages = self._prepare_messages(session)

        # Check for function calling needs
        function_results = await self._check_function_calls(content, session)
        if function_results:
            # Inject function results into context
            ai_messages.append({
                "role": "system",
                "content": f"Data retrieved: {function_results}"
            })

        # Get AI response
        response = await self.ai_service.chat(
            messages=ai_messages,
            feature="chat",
            max_tokens=2048
        )

        # Create response message
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            content=response.content,
            timestamp=datetime.utcnow(),
            metadata={
                "provider": response.provider.value,
                "tokens": response.input_tokens + response.output_tokens
            }
        )
        session.messages.append(assistant_message)
        session.last_activity = datetime.utcnow()

        return assistant_message

    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get session message history."""
        session = self._get_session(session_id)
        if not session:
            return []

        # Exclude system messages from history
        messages = [m for m in session.messages if m.role != MessageRole.SYSTEM]
        return messages[-limit:]

    def update_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> None:
        """Update session context with new data."""
        session = self._get_session(session_id)
        if session:
            session.context.update(context)

    def end_session(self, session_id: str) -> None:
        """End chat session."""
        session = self._get_session(session_id)
        if session:
            session.is_active = False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions. Returns count of cleaned sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.last_activity > self.SESSION_TIMEOUT
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    def _get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def _build_system_message(self, session: ChatSession) -> str:
        """Build system message with context."""
        context_parts = [
            "You are GanaPortal AI Assistant, helping users with their HR and business queries.",
            f"Company ID: {session.company_id}",
            f"User ID: {session.user_id}",
        ]

        if session.context:
            if "user_name" in session.context:
                context_parts.append(f"User Name: {session.context['user_name']}")
            if "user_role" in session.context:
                context_parts.append(f"User Role: {session.context['user_role']}")
            if "company_name" in session.context:
                context_parts.append(f"Company: {session.context['company_name']}")

        context_parts.extend([
            "",
            "You can help with:",
            "- Employee information and HR queries",
            "- Leave balance and requests",
            "- Payroll and salary queries",
            "- Invoice and payment status",
            "- Company policies and procedures",
            "",
            "Be helpful, accurate, and concise. Use Indian rupee (₹) for currency.",
            "If you need specific data, I'll retrieve it for you."
        ])

        return "\n".join(context_parts)

    def _prepare_messages(self, session: ChatSession) -> List[Dict[str, str]]:
        """Prepare messages for AI with context window management."""
        messages = []

        # Always include system message
        system_msg = next(
            (m for m in session.messages if m.role == MessageRole.SYSTEM),
            None
        )
        if system_msg:
            messages.append({"role": "system", "content": system_msg.content})

        # Add conversation history (limited to fit context window)
        history = [m for m in session.messages if m.role != MessageRole.SYSTEM]

        # Estimate tokens and trim if needed
        total_chars = sum(len(m.content) for m in history)
        while total_chars > self.MAX_CONTEXT_TOKENS * 4 and len(history) > 2:
            history.pop(0)
            total_chars = sum(len(m.content) for m in history)

        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        return messages

    async def _check_function_calls(
        self,
        content: str,
        session: ChatSession
    ) -> Optional[Dict[str, Any]]:
        """Check if message requires data retrieval."""
        content_lower = content.lower()

        results = {}

        # Check for employee queries
        if any(x in content_lower for x in ["my leave", "leave balance", "remaining leave"]):
            # In production, call actual service
            results["leave_balance"] = {
                "casual": 8,
                "earned": 12,
                "sick": 5,
                "total_used": 7
            }

        # Check for payroll queries
        if any(x in content_lower for x in ["my salary", "payslip", "salary slip"]):
            results["salary_info"] = {
                "basic": 50000,
                "hra": 20000,
                "total_gross": 85000,
                "net": 72000
            }

        # Check for attendance queries
        if "attendance" in content_lower:
            results["attendance"] = {
                "present_days": 22,
                "absent_days": 0,
                "half_days": 1,
                "work_from_home": 4
            }

        return results if results else None


class ChatSessionManager:
    """Manage multiple chat sessions across users."""

    def __init__(self):
        self._user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids

    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user."""
        return self._user_sessions.get(user_id, [])

    def register_session(self, user_id: str, session_id: str) -> None:
        """Register session for user."""
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = []
        self._user_sessions[user_id].append(session_id)

    def get_active_session_count(self) -> int:
        """Get total active session count."""
        return sum(len(sessions) for sessions in self._user_sessions.values())
