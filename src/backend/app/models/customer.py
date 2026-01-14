"""
Customer/Vendor Models - BE-022
Party master for AR/AP
"""
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PartyType(str, PyEnum):
    """Party type."""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    BOTH = "both"  # Can be both customer and vendor


class GSTRegistrationType(str, PyEnum):
    """GST registration type."""
    REGULAR = "regular"
    COMPOSITION = "composition"
    UNREGISTERED = "unregistered"
    SEZ = "sez"
    DEEMED_EXPORT = "deemed_export"


class PaymentTerms(str, PyEnum):
    """Payment terms."""
    IMMEDIATE = "immediate"
    NET_7 = "net_7"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    NET_90 = "net_90"
    CUSTOM = "custom"


class Party(Base):
    """Customer/Vendor master."""
    __tablename__ = "parties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Basic info
    code = Column(String(20), nullable=False)  # CUST-001, VEND-001
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    party_type = Column(Enum(PartyType), nullable=False)

    # Contact info
    email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))
    website = Column(String(255))

    # Tax details
    pan = Column(String(10))
    gstin = Column(String(15))
    gst_registration_type = Column(Enum(GSTRegistrationType), default=GSTRegistrationType.REGULAR)
    tan = Column(String(10))  # For TDS

    # TDS applicability
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(String(20))  # 194C, 194J, etc.
    tds_rate = Column(Numeric(5, 2))
    lower_deduction_certificate = Column(Boolean, default=False)
    ldc_rate = Column(Numeric(5, 2))
    ldc_valid_from = Column(DateTime)
    ldc_valid_to = Column(DateTime)
    ldc_certificate_number = Column(String(50))

    # Credit/Payment terms
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_days = Column(Integer, default=30)
    credit_limit = Column(Numeric(18, 2), default=0)

    # Pricing
    default_currency = Column(String(3), default="INR")
    price_list_id = Column(UUID(as_uuid=True))  # Default price list

    # Bank details (for payments)
    bank_name = Column(String(255))
    bank_account_number = Column(String(50))
    bank_ifsc = Column(String(20))
    bank_branch = Column(String(255))

    # Accounting
    receivable_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    payable_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Balances (denormalized for quick access)
    outstanding_receivable = Column(Numeric(18, 2), default=0)
    outstanding_payable = Column(Numeric(18, 2), default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_party_code'),
        UniqueConstraint('company_id', 'gstin', name='uq_company_party_gstin'),
    )


class PartyAddress(Base):
    """Party addresses (billing, shipping, etc.)."""
    __tablename__ = "party_addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)

    # Address type
    address_type = Column(String(20), nullable=False)  # billing, shipping, registered
    is_default = Column(Boolean, default=False)

    # Address details
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    state_code = Column(String(2))  # For GST (e.g., "29" for Karnataka)
    pincode = Column(String(10), nullable=False)
    country = Column(String(100), default="India")

    # GST place of supply
    gstin = Column(String(15))  # Can be different for different states

    # Contact
    contact_person = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    party = relationship("Party", backref="addresses")


class PartyContact(Base):
    """Party contact persons."""
    __tablename__ = "party_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)

    # Contact details
    name = Column(String(255), nullable=False)
    designation = Column(String(100))
    department = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))

    # Role
    is_primary = Column(Boolean, default=False)
    is_billing_contact = Column(Boolean, default=False)
    is_shipping_contact = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    party = relationship("Party", backref="contacts")


class Currency(Base):
    """Currency master."""
    __tablename__ = "currencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(3), unique=True, nullable=False)  # INR, USD, EUR
    name = Column(String(100), nullable=False)
    symbol = Column(String(10))  # ₹, $, €
    decimal_places = Column(Integer, default=2)

    # Exchange rate (to base currency INR)
    exchange_rate = Column(Numeric(18, 6), default=1)
    rate_date = Column(DateTime)

    # Status
    is_base = Column(Boolean, default=False)  # INR is base
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExchangeRate(Base):
    """Exchange rate history."""
    __tablename__ = "exchange_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(18, 6), nullable=False)
    rate_date = Column(DateTime, nullable=False)

    # Source
    source = Column(String(50))  # manual, rbi, oanda, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='uq_exchange_rate'),
    )
