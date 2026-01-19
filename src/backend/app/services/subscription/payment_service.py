"""
Payment Service
Payment gateway integration (Razorpay, PayU) and payment processing
"""
from typing import Optional, Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import datetime
import hashlib
import hmac
import json
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.datetime_utils import utc_now
from app.core.constants import PAYMENT_SERVICE_TIMEOUT
from app.models.subscription import (
    Subscription, SubscriptionInvoice, SubscriptionPayment,
    SubscriptionAuditLog,
    InvoiceStatus, PaymentStatus, PaymentMethod
)
from app.core.config import settings


class PaymentService:
    """
    Service for payment processing.
    Supports:
    - Razorpay integration (orders, payments, subscriptions)
    - PayU integration (alternate gateway)
    - Manual payment recording
    - Refund processing
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._razorpay_key = getattr(settings, 'RAZORPAY_KEY_ID', None)
        self._razorpay_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
        self._razorpay_base_url = "https://api.razorpay.com/v1"

    # =========================================================================
    # Razorpay Integration
    # =========================================================================

    async def create_razorpay_order(
        self,
        invoice_id: UUID,
        notes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order for an invoice.
        """
        invoice = await self.db.get(SubscriptionInvoice, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        if invoice.status in [InvoiceStatus.paid, InvoiceStatus.cancelled]:
            raise ValueError(f"Cannot create order for {invoice.status.value} invoice")

        # Amount in paise (Razorpay uses smallest currency unit)
        amount_paise = int(invoice.amount_due * 100)

        payload = {
            "amount": amount_paise,
            "currency": invoice.currency,
            "receipt": invoice.invoice_number,
            "notes": notes or {
                "invoice_id": str(invoice_id),
                "company_id": str(invoice.company_id),
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._razorpay_base_url}/orders",
                json=payload,
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Razorpay order creation failed: {response.text}")

            order = response.json()

        # Store order ID on invoice
        invoice.razorpay_order_id = order["id"]
        await self.db.commit()

        return {
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": invoice.currency,
            "key": self._razorpay_key,
            "invoice_number": invoice.invoice_number,
            "prefill": {
                "email": invoice.customer_email,
                "contact": "",  # Add if available
            },
            "notes": order.get("notes", {}),
        }

    async def verify_razorpay_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Dict[str, Any]:
        """
        Verify Razorpay payment signature and record payment.
        """
        # Verify signature
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            self._razorpay_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if razorpay_signature != expected_signature:
            raise ValueError("Invalid payment signature")

        # Get invoice by order ID
        invoice = await self.db.scalar(
            select(SubscriptionInvoice).where(
                SubscriptionInvoice.razorpay_order_id == razorpay_order_id
            )
        )

        if not invoice:
            raise ValueError("Invoice not found for order")

        # Fetch payment details from Razorpay
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self._razorpay_base_url}/payments/{razorpay_payment_id}",
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Failed to fetch payment details: {response.text}")

            payment_data = response.json()

        # Record payment
        payment = await self.record_payment(
            invoice_id=invoice.id,
            amount=Decimal(str(payment_data["amount"] / 100)),
            payment_method=PaymentMethod.razorpay,
            gateway_payment_id=razorpay_payment_id,
            gateway_data=payment_data,
        )

        return {
            "status": "success",
            "payment_id": str(payment.id),
            "payment_number": payment.payment_number,
            "amount": float(payment.amount),
            "invoice_status": invoice.status.value,
        }

    async def create_razorpay_subscription(
        self,
        subscription_id: UUID,
        plan_id: str,  # Razorpay plan ID
        customer_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Razorpay subscription for recurring billing.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        payload = {
            "plan_id": plan_id,
            "total_count": 12,  # 12 cycles
            "notes": {
                "subscription_id": str(subscription_id),
                "company_id": str(subscription.company_id),
            }
        }

        if customer_id:
            payload["customer_id"] = customer_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._razorpay_base_url}/subscriptions",
                json=payload,
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Razorpay subscription creation failed: {response.text}")

            rp_subscription = response.json()

        # Store Razorpay subscription ID
        subscription.razorpay_subscription_id = rp_subscription["id"]
        await self.db.commit()

        return {
            "subscription_id": rp_subscription["id"],
            "short_url": rp_subscription.get("short_url"),
            "status": rp_subscription["status"],
        }

    async def cancel_razorpay_subscription(
        self,
        subscription_id: UUID,
        cancel_at_cycle_end: bool = True,
    ) -> Dict[str, Any]:
        """
        Cancel a Razorpay subscription.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        if not subscription.razorpay_subscription_id:
            raise ValueError("No Razorpay subscription linked")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._razorpay_base_url}/subscriptions/{subscription.razorpay_subscription_id}/cancel",
                json={"cancel_at_cycle_end": cancel_at_cycle_end},
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Failed to cancel Razorpay subscription: {response.text}")

            result = response.json()

        return {
            "status": result["status"],
            "cancelled_at": result.get("cancelled_at"),
        }

    # =========================================================================
    # Generic Payment Recording
    # =========================================================================

    async def record_payment(
        self,
        invoice_id: UUID,
        amount: Decimal,
        payment_method: PaymentMethod,
        gateway_payment_id: Optional[str] = None,
        bank_reference: Optional[str] = None,
        upi_transaction_id: Optional[str] = None,
        cheque_number: Optional[str] = None,
        gateway_data: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionPayment:
        """
        Record a payment against an invoice.
        """
        invoice = await self.db.get(SubscriptionInvoice, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        # Generate payment number
        count = await self.db.scalar(
            select(func.count(SubscriptionPayment.id)).where(
                SubscriptionPayment.company_id == invoice.company_id
            )
        )
        payment_number = f"PAY-{invoice.company_id.hex[:8].upper()}-{(count or 0) + 1:06d}"

        # Determine gateway
        gateway = None
        if payment_method == PaymentMethod.razorpay:
            gateway = "razorpay"
        elif payment_method == PaymentMethod.payu:
            gateway = "payu"
        elif payment_method == PaymentMethod.stripe:
            gateway = "stripe"

        payment = SubscriptionPayment(
            invoice_id=invoice_id,
            company_id=invoice.company_id,
            payment_number=payment_number,
            payment_date=utc_now(),
            amount=amount,
            currency=invoice.currency,
            payment_method=payment_method.value,
            payment_gateway=gateway,
            gateway_payment_id=gateway_payment_id,
            status=PaymentStatus.completed,
            bank_reference=bank_reference,
            upi_transaction_id=upi_transaction_id,
            cheque_number=cheque_number,
            gateway_response=gateway_data,
        )

        self.db.add(payment)

        # Update invoice
        invoice.amount_paid = (invoice.amount_paid or Decimal("0")) + amount
        invoice.amount_due = invoice.total_amount - invoice.amount_paid

        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.paid
            invoice.paid_at = utc_now()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.partially_paid

        # Audit log
        audit = SubscriptionAuditLog(
            subscription_id=invoice.subscription_id,
            action="payment_recorded",
            details={
                "payment_number": payment_number,
                "amount": str(amount),
                "payment_method": payment_method.value,
                "invoice_number": invoice.invoice_number,
            }
        )
        self.db.add(audit)

        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def process_refund(
        self,
        payment_id: UUID,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a refund for a payment.
        """
        payment = await self.db.get(SubscriptionPayment, payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.status != PaymentStatus.completed:
            raise ValueError("Can only refund completed payments")

        refund_amount = amount or payment.amount

        if refund_amount > (payment.amount - (payment.refund_amount or Decimal("0"))):
            raise ValueError("Refund amount exceeds available amount")

        # Process gateway refund if applicable
        if payment.payment_gateway == "razorpay" and payment.gateway_payment_id:
            await self._process_razorpay_refund(
                payment.gateway_payment_id,
                refund_amount,
            )

        # Update payment record
        payment.refund_amount = (payment.refund_amount or Decimal("0")) + refund_amount

        if payment.refund_amount >= payment.amount:
            payment.status = PaymentStatus.refunded

        # Update invoice
        invoice = await self.db.get(SubscriptionInvoice, payment.invoice_id)
        if invoice:
            invoice.amount_paid = (invoice.amount_paid or Decimal("0")) - refund_amount
            invoice.amount_due = invoice.total_amount - invoice.amount_paid

            if invoice.amount_paid <= 0:
                invoice.status = InvoiceStatus.refunded
            elif invoice.amount_due > 0:
                invoice.status = InvoiceStatus.partially_paid

        # Audit log
        audit = SubscriptionAuditLog(
            subscription_id=invoice.subscription_id if invoice else None,
            action="refund_processed",
            details={
                "payment_id": str(payment_id),
                "refund_amount": str(refund_amount),
                "reason": reason,
            }
        )
        self.db.add(audit)

        await self.db.commit()

        return {
            "status": "refunded",
            "refund_amount": float(refund_amount),
            "payment_status": payment.status.value,
        }

    async def _process_razorpay_refund(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> Dict[str, Any]:
        """Process refund through Razorpay."""
        amount_paise = int(amount * 100)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._razorpay_base_url}/payments/{payment_id}/refund",
                json={"amount": amount_paise},
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Razorpay refund failed: {response.text}")

            return response.json()

    # =========================================================================
    # Payment Queries
    # =========================================================================

    async def get_payment_history(
        self,
        company_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get payment history for a company."""
        query = select(SubscriptionPayment).where(
            SubscriptionPayment.company_id == company_id
        ).order_by(SubscriptionPayment.payment_date.desc()).limit(limit)

        result = await self.db.execute(query)
        payments = result.scalars().all()

        return [
            {
                "id": str(p.id),
                "payment_number": p.payment_number,
                "payment_date": p.payment_date.isoformat(),
                "amount": float(p.amount),
                "currency": p.currency,
                "payment_method": p.payment_method,
                "status": p.status.value,
                "invoice_id": str(p.invoice_id),
            }
            for p in payments
        ]

    async def get_outstanding_invoices(
        self,
        company_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """Get all outstanding (unpaid/partially paid) invoices."""
        query = select(SubscriptionInvoice).where(
            SubscriptionInvoice.status.in_([
                InvoiceStatus.pending,
                InvoiceStatus.partially_paid,
                InvoiceStatus.overdue
            ])
        )

        if company_id:
            query = query.where(SubscriptionInvoice.company_id == company_id)

        query = query.order_by(SubscriptionInvoice.due_date)

        result = await self.db.execute(query)
        invoices = result.scalars().all()

        return [
            {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "company_id": str(inv.company_id),
                "customer_name": inv.customer_name,
                "invoice_date": inv.invoice_date.isoformat(),
                "due_date": inv.due_date.isoformat(),
                "total_amount": float(inv.total_amount),
                "amount_paid": float(inv.amount_paid),
                "amount_due": float(inv.amount_due),
                "status": inv.status.value,
                "days_overdue": (utc_now().date() - inv.due_date).days
                    if utc_now().date() > inv.due_date else 0,
            }
            for inv in invoices
        ]

    async def mark_invoice_overdue(self) -> int:
        """
        Mark overdue invoices (past due date and not fully paid).
        Called by scheduler.
        """
        today = utc_now().date()

        query = select(SubscriptionInvoice).where(
            and_(
                SubscriptionInvoice.status.in_([
                    InvoiceStatus.pending,
                    InvoiceStatus.partially_paid
                ]),
                SubscriptionInvoice.due_date < today
            )
        )

        result = await self.db.execute(query)
        invoices = result.scalars().all()

        count = 0
        for invoice in invoices:
            invoice.status = InvoiceStatus.overdue
            count += 1

        await self.db.commit()
        return count

    # =========================================================================
    # Payment Link Generation
    # =========================================================================

    async def generate_payment_link(
        self,
        invoice_id: UUID,
        expire_by: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a shareable payment link for an invoice.
        """
        invoice = await self.db.get(SubscriptionInvoice, invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        amount_paise = int(invoice.amount_due * 100)

        payload = {
            "amount": amount_paise,
            "currency": invoice.currency,
            "accept_partial": True,
            "first_min_partial_amount": 100,  # Minimum ₹1
            "description": f"Payment for Invoice {invoice.invoice_number}",
            "customer": {
                "email": invoice.customer_email or "",
                "name": invoice.customer_name,
            },
            "notify": {
                "email": True,
                "sms": False,
            },
            "reminder_enable": True,
            "notes": {
                "invoice_id": str(invoice_id),
                "invoice_number": invoice.invoice_number,
            },
            "callback_url": "",  # Add callback URL
            "callback_method": "get",
        }

        if expire_by:
            payload["expire_by"] = int(expire_by.timestamp())

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._razorpay_base_url}/payment_links",
                json=payload,
                auth=(self._razorpay_key, self._razorpay_secret),
                timeout=PAYMENT_SERVICE_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(f"Payment link creation failed: {response.text}")

            link_data = response.json()

        # Store payment link on invoice
        invoice.payment_link = link_data.get("short_url")
        await self.db.commit()

        return {
            "payment_link_id": link_data["id"],
            "short_url": link_data["short_url"],
            "amount": amount_paise,
            "status": link_data["status"],
        }
