"""
Currency and Exchange Rate models.
WBS Reference: Phase 12 - Multi-Currency Support
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    Numeric, ForeignKey, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.models.base import BaseModel


class ExchangeRateSource(str, enum.Enum):
    """Source of exchange rate."""
    MANUAL = "manual"
    RBI = "rbi"
    FOREX_API = "forex_api"
    BANK = "bank"


class Currency(BaseModel):
    """Currency master data."""
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)  # ISO 4217 code
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)

    # Flags
    is_base_currency: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Display
    symbol_position: Mapped[str] = mapped_column(String(10), default="before")  # before or after
    thousands_separator: Mapped[str] = mapped_column(String(1), default=",")
    decimal_separator: Mapped[str] = mapped_column(String(1), default=".")

    # Relationships
    exchange_rates_from: Mapped[List["ExchangeRate"]] = relationship(
        back_populates="from_currency_rel",
        foreign_keys="ExchangeRate.from_currency",
    )
    exchange_rates_to: Mapped[List["ExchangeRate"]] = relationship(
        back_populates="to_currency_rel",
        foreign_keys="ExchangeRate.to_currency",
    )


class ExchangeRate(BaseModel):
    """Exchange rate records."""
    __tablename__ = "exchange_rates"

    from_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code"), nullable=False
    )
    to_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code"), nullable=False
    )

    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    rate_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Source
    source: Mapped[ExchangeRateSource] = mapped_column(
        SQLEnum(ExchangeRateSource), default=ExchangeRateSource.MANUAL
    )

    # For auditing
    entered_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    from_currency_rel: Mapped["Currency"] = relationship(
        back_populates="exchange_rates_from",
        foreign_keys=[from_currency],
    )
    to_currency_rel: Mapped["Currency"] = relationship(
        back_populates="exchange_rates_to",
        foreign_keys=[to_currency],
    )

    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", "rate_date", name="uq_rate_date"),
    )


class ForexTransaction(BaseModel):
    """Forex gain/loss tracking for transactions."""
    __tablename__ = "forex_transactions"

    # Reference to original transaction
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)  # invoice, payment, etc.
    reference_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    # Currency details
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    original_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    original_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    original_base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Settlement
    settlement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    settlement_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 8), nullable=True)
    settlement_base_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

    # Gain/Loss (positive = gain, negative = loss)
    forex_gain_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

    # Journal entry for gain/loss
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )

    is_settled: Mapped[bool] = mapped_column(Boolean, default=False)
