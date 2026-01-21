"""
Multi-Currency Schemas (MOD-19)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class ExchangeRateSource(str, Enum):
    MANUAL = "manual"
    RBI = "rbi"
    OANDA = "oanda"
    XE = "xe"
    CUSTOM_API = "custom_api"


class ExchangeRateType(str, Enum):
    SPOT = "spot"
    FORWARD = "forward"
    AVERAGE = "average"
    CLOSING = "closing"


# ============ Currency Schemas ============

class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str
    decimal_places: int = 2
    symbol_position: str = "before"
    thousand_separator: str = ","
    decimal_separator: str = "."
    is_active: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimal_places: Optional[int] = None
    symbol_position: Optional[str] = None
    thousand_separator: Optional[str] = None
    decimal_separator: Optional[str] = None
    is_active: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    id: UUID
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Company Currency Schemas ============

class CompanyCurrencyBase(BaseModel):
    currency_id: UUID
    is_functional: bool = False
    is_reporting: bool = False
    is_active: bool = True


class CompanyCurrencyCreate(CompanyCurrencyBase):
    pass


class CompanyCurrencyUpdate(BaseModel):
    is_functional: Optional[bool] = None
    is_reporting: Optional[bool] = None
    is_active: Optional[bool] = None


class CompanyCurrencyResponse(CompanyCurrencyBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Exchange Rate Schemas ============

class ExchangeRateBase(BaseModel):
    from_currency_id: UUID
    to_currency_id: UUID
    rate_type: ExchangeRateType = ExchangeRateType.SPOT
    rate: Decimal
    inverse_rate: Optional[Decimal] = None
    effective_date: date
    expiry_date: Optional[date] = None
    source: ExchangeRateSource = ExchangeRateSource.MANUAL
    is_active: bool = True


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateUpdate(BaseModel):
    rate: Optional[Decimal] = None
    inverse_rate: Optional[Decimal] = None
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class ExchangeRateResponse(ExchangeRateBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Exchange Rate History Schemas ============

class ExchangeRateHistoryBase(BaseModel):
    from_currency_id: UUID
    to_currency_id: UUID
    rate_type: ExchangeRateType
    rate: Decimal
    rate_date: date
    source: ExchangeRateSource


class ExchangeRateHistoryCreate(ExchangeRateHistoryBase):
    pass


class ExchangeRateHistoryResponse(ExchangeRateHistoryBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Currency Revaluation Schemas ============

class CurrencyRevaluationItemBase(BaseModel):
    account_id: UUID
    currency_id: UUID
    original_amount: Decimal
    original_rate: Decimal
    original_base_amount: Decimal
    new_rate: Decimal
    new_base_amount: Decimal
    gain_loss: Decimal


class CurrencyRevaluationItemCreate(CurrencyRevaluationItemBase):
    pass


class CurrencyRevaluationItemResponse(CurrencyRevaluationItemBase):
    id: UUID
    revaluation_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CurrencyRevaluationBase(BaseModel):
    revaluation_date: date
    rate_type: ExchangeRateType
    description: Optional[str] = None


class CurrencyRevaluationCreate(CurrencyRevaluationBase):
    items: Optional[List[CurrencyRevaluationItemCreate]] = None


class CurrencyRevaluationUpdate(BaseModel):
    description: Optional[str] = None


class CurrencyRevaluationResponse(CurrencyRevaluationBase):
    id: UUID
    company_id: UUID
    revaluation_number: str
    status: str
    total_gain_loss: Decimal
    journal_entry_id: Optional[UUID] = None
    posted_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[CurrencyRevaluationItemResponse] = []

    model_config = {"from_attributes": True}


# ============ Currency Conversion Schemas ============

class CurrencyConversionRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal
    rate_date: Optional[date] = None
    rate_type: ExchangeRateType = ExchangeRateType.SPOT


class CurrencyConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: Decimal
    converted_amount: Decimal
    exchange_rate: Decimal
    rate_date: date
    rate_type: ExchangeRateType


# List Response Schemas
class CurrencyListResponse(BaseModel):
    items: List[CurrencyResponse]
    total: int
    page: int
    size: int


class CompanyCurrencyListResponse(BaseModel):
    items: List[CompanyCurrencyResponse]
    total: int
    page: int
    size: int


class ExchangeRateListResponse(BaseModel):
    items: List[ExchangeRateResponse]
    total: int
    page: int
    size: int


class ExchangeRateHistoryListResponse(BaseModel):
    items: List[ExchangeRateHistoryResponse]
    total: int
    page: int
    size: int


class CurrencyRevaluationListResponse(BaseModel):
    items: List[CurrencyRevaluationResponse]
    total: int
    page: int
    size: int


# ============ Rate Lookup Schemas ============

class RateLookupRequest(BaseModel):
    """Request to look up an exchange rate"""
    from_currency: str
    to_currency: str
    rate_date: Optional[date] = None
    rate_type: ExchangeRateType = ExchangeRateType.SPOT


class RateLookupResponse(BaseModel):
    """Exchange rate lookup response"""
    from_currency: str
    to_currency: str
    rate: Decimal
    inverse_rate: Decimal
    rate_date: date
    rate_type: ExchangeRateType
    source: ExchangeRateSource
    is_estimated: bool = False


# ============ Revaluation Preview Schemas ============

class RevaluationPreviewRequest(BaseModel):
    """Request to preview a revaluation"""
    revaluation_date: date
    rate_type: ExchangeRateType = ExchangeRateType.SPOT
    currency_ids: Optional[List[UUID]] = None


class RevaluationPreviewItem(BaseModel):
    """Preview item for revaluation"""
    account_id: UUID
    account_code: str
    account_name: str
    currency_code: str
    original_amount: Decimal
    original_rate: Decimal
    original_base_amount: Decimal
    new_rate: Decimal
    new_base_amount: Decimal
    gain_loss: Decimal


class RevaluationPreviewResponse(BaseModel):
    """Response for revaluation preview"""
    revaluation_date: date
    rate_type: ExchangeRateType
    items: List[RevaluationPreviewItem]
    total_gain_loss: Decimal
    affected_accounts: int


# Aliases for endpoint compatibility
RevaluationListResponse = CurrencyRevaluationListResponse
