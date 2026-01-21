"""
Multi-Currency Models (MOD-19)
Exchange rates, currency conversion, multi-currency transactions
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class ExchangeRateSource(str, enum.Enum):
    RBI = "rbi"  # Reserve Bank of India
    MANUAL = "manual"
    API = "api"
    BANK = "bank"


class ExchangeRateType(str, enum.Enum):
    SPOT = "spot"
    FORWARD = "forward"
    BUYING = "buying"
    SELLING = "selling"


# ============ Currency Master ============

class Currency(Base, TimestampMixin, SoftDeleteMixin):
    """Currency master"""
    __tablename__ = "currencies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    code: Mapped[str] = mapped_column(String(10), unique=True)  # ISO 4217 code
    name: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(10))

    # Format
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)
    decimal_separator: Mapped[str] = mapped_column(String(5), default=".")
    thousand_separator: Mapped[str] = mapped_column(String(5), default=",")
    symbol_position: Mapped[str] = mapped_column(String(20), default="before")  # before/after

    # Country
    country_code: Mapped[Optional[str]] = mapped_column(String(10))
    country_name: Mapped[Optional[str]] = mapped_column(String(100))

    is_base_currency: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    exchange_rates: Mapped[List["ExchangeRate"]] = relationship(back_populates="currency")


class CompanyCurrency(Base, TimestampMixin):
    """Company-enabled currencies"""
    __tablename__ = "company_currencies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    currency_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("currencies.id"))

    is_base_currency: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reporting_currency: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Rounding
    rounding_method: Mapped[str] = mapped_column(String(50), default="round_half_up")


# ============ Exchange Rates ============

class ExchangeRate(Base, TimestampMixin):
    """Exchange rates"""
    __tablename__ = "exchange_rates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    currency_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("currencies.id"))
    base_currency_code: Mapped[str] = mapped_column(String(10), default="INR")

    rate_date: Mapped[date] = mapped_column(Date)
    rate_type: Mapped[ExchangeRateType] = mapped_column(SQLEnum(ExchangeRateType), default=ExchangeRateType.SPOT)

    # Rates
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8))  # 1 foreign = X base
    inverse_rate: Mapped[float] = mapped_column(Numeric(18, 8))   # 1 base = X foreign

    # Buy/Sell spread
    buying_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    selling_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))

    source: Mapped[ExchangeRateSource] = mapped_column(SQLEnum(ExchangeRateSource), default=ExchangeRateSource.MANUAL)
    source_reference: Mapped[Optional[str]] = mapped_column(String(200))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    currency: Mapped["Currency"] = relationship(back_populates="exchange_rates")


class ExchangeRateHistory(Base, TimestampMixin):
    """Historical exchange rate records"""
    __tablename__ = "exchange_rate_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    from_currency: Mapped[str] = mapped_column(String(10))
    to_currency: Mapped[str] = mapped_column(String(10))

    rate_date: Mapped[date] = mapped_column(Date)
    rate_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    open_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    close_rate: Mapped[float] = mapped_column(Numeric(18, 8))
    high_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))
    low_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 8))

    source: Mapped[str] = mapped_column(String(50))


# ============ Currency Revaluation ============

class CurrencyRevaluation(Base, TimestampMixin):
    """Foreign currency revaluation records"""
    __tablename__ = "currency_revaluations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    revaluation_number: Mapped[str] = mapped_column(String(50), unique=True)
    revaluation_date: Mapped[date] = mapped_column(Date)

    currency_code: Mapped[str] = mapped_column(String(10))
    old_rate: Mapped[float] = mapped_column(Numeric(18, 8))
    new_rate: Mapped[float] = mapped_column(Numeric(18, 8))

    # Impact
    total_foreign_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    old_base_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    new_base_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    gain_loss: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Accounting
    gain_loss_account: Mapped[Optional[str]] = mapped_column(String(100))
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/posted/reversed
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    posted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    items: Mapped[List["CurrencyRevaluationItem"]] = relationship(back_populates="revaluation")


class CurrencyRevaluationItem(Base, TimestampMixin):
    """Revaluation line items by account"""
    __tablename__ = "currency_revaluation_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    revaluation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("currency_revaluations.id"))

    account_code: Mapped[str] = mapped_column(String(100))
    account_name: Mapped[str] = mapped_column(String(500))
    account_type: Mapped[str] = mapped_column(String(50))  # receivable/payable/bank

    # Party (if applicable)
    party_type: Mapped[Optional[str]] = mapped_column(String(50))  # customer/supplier
    party_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    party_name: Mapped[Optional[str]] = mapped_column(String(500))

    # Balances
    foreign_balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    old_base_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    new_base_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    gain_loss: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Relationships
    revaluation: Mapped["CurrencyRevaluation"] = relationship(back_populates="items")
