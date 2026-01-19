"""
AI Services Package - Phase 7 AI Integration
AI-001 through AI-012 implementations
"""
from app.services.ai.ai_service import AIService, AIProvider, AIResponse
from app.services.ai.document_ai import DocumentAIService, DocumentType, ExtractionResult
from app.services.ai.categorization import (
    TransactionCategorizationService,
    TransactionCategory,
    CategorizationResult
)
from app.services.ai.nl_to_sql import NLToSQLService, QueryIntent, SQLGenerationResult
from app.services.ai.chat_service import (
    ChatService,
    ChatSession,
    ChatMessage,
    ChatSessionManager,
    MessageRole
)
from app.services.ai.digest_service import (
    DigestService,
    DailyDigest,
    DigestItem,
    DigestSection,
    DigestType
)
from app.services.ai.anomaly_detection import (
    AnomalyDetectionService,
    SmartSuggestionService,
    Anomaly,
    AnomalyType,
    AnomalySeverity,
    SmartSuggestion,
    SuggestionType
)
from app.services.ai.automation import (
    AutoActionService,
    TaskQueueService,
    AutoAction,
    ActionType,
    ActionStatus,
    TriggerType,
    QueueTask,
    QueuePriority
)

__all__ = [
    # AI-001: Core AI Service
    "AIService",
    "AIProvider",
    "AIResponse",

    # AI-002: Document OCR/Vision
    "DocumentAIService",
    "DocumentType",
    "ExtractionResult",

    # AI-003, AI-004: Categorization & Confidence
    "TransactionCategorizationService",
    "TransactionCategory",
    "CategorizationResult",

    # AI-005: NL to SQL
    "NLToSQLService",
    "QueryIntent",
    "SQLGenerationResult",

    # AI-006: Chat Service
    "ChatService",
    "ChatSession",
    "ChatMessage",
    "ChatSessionManager",
    "MessageRole",

    # AI-007, AI-008: Digest & Learning
    "DigestService",
    "DailyDigest",
    "DigestItem",
    "DigestSection",
    "DigestType",

    # AI-009: Anomaly Detection
    "AnomalyDetectionService",
    "Anomaly",
    "AnomalyType",
    "AnomalySeverity",

    # AI-010: Smart Suggestions
    "SmartSuggestionService",
    "SmartSuggestion",
    "SuggestionType",

    # AI-011: Auto-Actions
    "AutoActionService",
    "AutoAction",
    "ActionType",
    "ActionStatus",
    "TriggerType",

    # AI-012: Queue Management
    "TaskQueueService",
    "QueueTask",
    "QueuePriority",
]
