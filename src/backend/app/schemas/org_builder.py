"""
AI Org Builder Schemas - Pydantic models for AI-powered organizational structure
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class RecommendationType(str, Enum):
    initial_structure = "initial_structure"
    role_addition = "role_addition"
    restructure = "restructure"
    scaling = "scaling"


class RecommendationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    merged = "merged"
    expired = "expired"


class RecommendationItemType(str, Enum):
    department = "department"
    designation = "designation"
    role_change = "role_change"


class RecommendationItemAction(str, Enum):
    create = "create"
    modify = "modify"
    remove = "remove"
    merge = "merge"


class RecommendationItemStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    applied = "applied"


# =============================================================================
# Department Recommendation Data
# =============================================================================

class DepartmentRecommendation(BaseModel):
    """Recommended department structure."""
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    headcount_target: Optional[int] = None
    parent_department: Optional[str] = None  # Name of parent department if hierarchical
    rationale: Optional[str] = None


# =============================================================================
# Designation/Role Recommendation Data
# =============================================================================

class DesignationRecommendation(BaseModel):
    """Recommended designation/role with JD."""
    name: str
    code: Optional[str] = None
    department: str  # Department name this role belongs to
    level: Optional[int] = None  # 1=C-suite, 2=VP, 3=Director, 4=Manager, 5=Senior, 6=Mid, 7=Junior
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: int = 0
    experience_max: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    headcount_target: int = 1
    priority: str = "normal"  # immediate, next_quarter, nice_to_have
    rationale: Optional[str] = None


# =============================================================================
# Full Recommendation Structure
# =============================================================================

class OrgStructureRecommendation(BaseModel):
    """Complete organization structure recommendation."""
    departments: List[DepartmentRecommendation] = []
    designations: List[DesignationRecommendation] = []
    summary: str
    total_headcount: int
    estimated_monthly_cost: Optional[Decimal] = None


# =============================================================================
# AI Recommendation Schemas
# =============================================================================

class AIRecommendationCreate(BaseModel):
    """Create a new AI recommendation."""
    recommendation_type: str
    trigger_event: Optional[str] = None
    trigger_entity_id: Optional[UUID] = None
    trigger_entity_type: Optional[str] = None
    priority: int = 5
    confidence_score: Optional[Decimal] = None
    recommendation_data: Dict[str, Any]
    rationale: Optional[str] = None
    ai_model_used: Optional[str] = None


class AIRecommendationResponse(BaseModel):
    """Response for AI recommendation."""
    id: UUID
    company_id: UUID
    recommendation_type: str
    status: str
    trigger_event: Optional[str]
    trigger_entity_id: Optional[UUID]
    trigger_entity_type: Optional[str]
    priority: int
    confidence_score: Optional[Decimal]
    recommendation_data: Dict[str, Any]
    rationale: Optional[str]
    ai_model_used: Optional[str]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    user_feedback: Optional[str]
    user_modifications: Optional[Dict[str, Any]]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items_count: int = 0
    items_pending: int = 0
    items_accepted: int = 0

    class Config:
        from_attributes = True


class AIRecommendationItemResponse(BaseModel):
    """Response for recommendation item."""
    id: UUID
    recommendation_id: UUID
    item_type: str
    action: str
    item_data: Dict[str, Any]
    status: str
    priority: int
    sequence_order: int
    depends_on: Optional[UUID]
    applied_entity_id: Optional[UUID]
    applied_entity_type: Optional[str]
    applied_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AIRecommendationDetailResponse(AIRecommendationResponse):
    """Detailed response with items."""
    items: List[AIRecommendationItemResponse] = []


class AIRecommendationListResponse(BaseModel):
    """Paginated list of recommendations."""
    success: bool = True
    data: List[AIRecommendationResponse]
    meta: dict


# =============================================================================
# User Action Schemas
# =============================================================================

class AcceptRecommendationRequest(BaseModel):
    """Request to accept entire recommendation."""
    user_feedback: Optional[str] = None


class RejectRecommendationRequest(BaseModel):
    """Request to reject recommendation."""
    rejection_reason: str


class AcceptItemRequest(BaseModel):
    """Request to accept individual item."""
    modifications: Optional[Dict[str, Any]] = None


class RejectItemRequest(BaseModel):
    """Request to reject individual item."""
    rejection_reason: str


class CustomizeRecommendationRequest(BaseModel):
    """Request to customize recommendation before accepting."""
    modifications: Dict[str, Any]  # Changes to recommendation_data
    items_to_accept: List[UUID] = []  # IDs of items to accept
    items_to_reject: List[UUID] = []  # IDs of items to reject
    user_feedback: Optional[str] = None


# =============================================================================
# Generation Request/Response Schemas
# =============================================================================

class GenerateOrgStructureRequest(BaseModel):
    """Request to generate organization structure."""
    include_departments: bool = True
    include_designations: bool = True
    include_salary_ranges: bool = True
    target_headcount: Optional[int] = None
    focus_products: Optional[List[UUID]] = None  # Specific products to focus on
    additional_context: Optional[str] = None


class GenerateOrgStructureResponse(BaseModel):
    """Response after generating org structure."""
    success: bool
    message: str
    recommendation_id: UUID
    preview: OrgStructureRecommendation


class PreviewOrgStructureRequest(BaseModel):
    """Request for preview without saving."""
    target_headcount: Optional[int] = None
    focus_products: Optional[List[UUID]] = None
    additional_context: Optional[str] = None


class PreviewOrgStructureResponse(BaseModel):
    """Preview response (not saved to DB)."""
    success: bool
    preview: OrgStructureRecommendation


# =============================================================================
# Designation JD Generation
# =============================================================================

class GenerateDesignationJDRequest(BaseModel):
    """Request to generate JD for a designation."""
    title: str
    department: Optional[str] = None
    level: Optional[int] = None
    additional_context: Optional[str] = None


class GenerateDesignationJDResponse(BaseModel):
    """Generated JD response."""
    success: bool
    title: str
    description: str
    requirements: str
    responsibilities: str
    skills_required: str
    experience_min: int
    experience_max: int
    salary_min: Decimal
    salary_max: Decimal


# =============================================================================
# Dashboard Summary
# =============================================================================

class OrgBuilderDashboardSummary(BaseModel):
    """Summary for dashboard widget."""
    pending_recommendations: int
    total_departments: int
    total_designations: int
    ai_generated_departments: int
    ai_generated_designations: int
    headcount_current: int
    headcount_target: int
    recent_recommendations: List[AIRecommendationResponse] = []


class PendingSuggestion(BaseModel):
    """A pending suggestion for quick action."""
    id: UUID
    type: str  # recommendation or item
    title: str
    description: str
    priority: int
    created_at: datetime


class PendingSuggestionsResponse(BaseModel):
    """List of pending suggestions."""
    success: bool = True
    data: List[PendingSuggestion]
    total: int
