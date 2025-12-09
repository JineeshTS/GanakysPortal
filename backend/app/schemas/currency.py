"""
Currency and Exchange Rate schemas.
WBS Reference: Phase 12 - Multi-Currency Support
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.currency import ExchangeRateSource


# Currency Schemas

class CurrencyBase(BaseModel):
    """Base currency schema."""
    code: str = Field(..., min_length=3, max_length=3)
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    decimal_places: int = 2
    symbol_position: str = "before"
    thousands_separator: str = ","
    decimal_separator: str = "."


class CurrencyCreate(CurrencyBase):
    """Schema for creating currency."""
    is_base_currency: bool = False


class CurrencyUpdate(BaseModel):
    """Schema for updating currency."""
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimal_places: Optional[int] = None
    symbol_position: Optional[str] = None
    thousands_separator: Optional[str] = None
    decimal_separator: Optional[str] = None
    is_active: Optional[bool] = None


class CurrencyResponse(CurrencyBase):
    """Schema for currency response."""
    id: UUID
    is_base_currency: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Exchange Rate Schemas

class ExchangeRateBase(BaseModel):
    """Base exchange rate schema."""
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate: Decimal = Field(..., gt=0)
    rate_date: date


class ExchangeRateCreate(ExchangeRateBase):
    """Schema for creating exchange rate."""
    source: ExchangeRateSource = ExchangeRateSource.MANUAL


class ExchangeRateResponse(ExchangeRateBase):
    """Schema for exchange rate response."""
    id: UUID
    source: ExchangeRateSource
    entered_by_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExchangeRateHistory(BaseModel):
    """Schema for exchange rate history."""
    from_currency: str
    to_currency: str
    rates: List[ExchangeRateResponse]


# Currency Conversion Schemas

class CurrencyConvertRequest(BaseModel):
    """Schema for currency conversion request."""
    amount: Decimal
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate_date: Optional[date] = None  # Uses latest if not provided


class CurrencyConvertResponse(BaseModel):
    """Schema for currency conversion response."""
    original_amount: Decimal
    from_currency: str
    to_currency: str
    rate: Decimal
    rate_date: date
    converted_amount: Decimal


# Forex Transaction Schemas

class ForexTransactionBase(BaseModel):
    """Base forex transaction schema."""
    reference_type: str
    reference_id: UUID
    currency: str
    original_amount: Decimal
    original_rate: Decimal


class ForexTransactionCreate(ForexTransactionBase):
    """Schema for creating forex transaction."""
    pass


class ForexTransactionSettle(BaseModel):
    """Schema for settling forex transaction."""
    settlement_date: date
    settlement_rate: Decimal


class ForexTransactionResponse(ForexTransactionBase):
    """Schema for forex transaction response."""
    id: UUID
    original_base_amount: Decimal
    settlement_date: Optional[date]
    settlement_rate: Optional[Decimal]
    settlement_base_amount: Optional[Decimal]
    forex_gain_loss: Optional[Decimal]
    journal_entry_id: Optional[UUID]
    is_settled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Dashboard/Summary Schemas

class CurrencyDashboard(BaseModel):
    """Schema for currency dashboard."""
    base_currency: str
    active_currencies: int
    latest_rates: List[ExchangeRateResponse]
    unrealized_forex_gain_loss: Decimal
    realized_forex_gain_loss: Decimal
