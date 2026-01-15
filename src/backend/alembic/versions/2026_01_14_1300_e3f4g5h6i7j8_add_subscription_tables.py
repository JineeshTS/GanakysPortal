"""add_subscription_tables

Revision ID: e3f4g5h6i7j8
Revises: d2e3f4g5h6i7
Create Date: 2026-01-14 13:00:00.000000

Subscription & Billing Module (MOD-01):
- Subscription plans with employee-based pricing
- Company subscriptions with billing cycles
- Invoices with GST compliance
- Payment tracking (Razorpay, PayU, bank transfer)
- Usage metering for API calls, AI queries, storage
- Discount codes and promotional offers
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e3f4g5h6i7j8'
down_revision: Union[str, None] = 'd2e3f4g5h6i7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # 1. Create subscription_plans table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            plan_type VARCHAR(30) DEFAULT 'professional',

            -- Pricing
            base_price_monthly DECIMAL(12, 2) NOT NULL DEFAULT 0,
            per_employee_monthly DECIMAL(10, 2) NOT NULL DEFAULT 0,
            base_price_annual DECIMAL(12, 2),
            per_employee_annual DECIMAL(10, 2),
            currency VARCHAR(3) DEFAULT 'INR',

            -- Employee Tiers (JSON)
            employee_tiers JSONB DEFAULT '[]',

            -- Feature Limits
            max_employees INTEGER,
            max_users INTEGER,
            max_companies INTEGER DEFAULT 1,
            storage_gb INTEGER DEFAULT 10,
            api_calls_monthly INTEGER DEFAULT 10000,
            ai_queries_monthly INTEGER DEFAULT 100,

            -- Feature Flags
            features JSONB DEFAULT '{}',
            modules_enabled TEXT[] DEFAULT '{}',

            -- Trial
            trial_days INTEGER DEFAULT 14,
            trial_features JSONB DEFAULT '{}',

            -- Metadata
            is_active BOOLEAN DEFAULT TRUE,
            is_public BOOLEAN DEFAULT TRUE,
            display_order INTEGER DEFAULT 0,
            highlight_text VARCHAR(100),

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_subscription_plans_code ON subscription_plans(code);
        CREATE INDEX idx_subscription_plans_type ON subscription_plans(plan_type);
        CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active);
    """)

    # =========================================================================
    # 2. Create pricing_tiers table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS pricing_tiers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            plan_id UUID NOT NULL REFERENCES subscription_plans(id) ON DELETE CASCADE,

            min_employees INTEGER NOT NULL,
            max_employees INTEGER,
            price_per_employee DECIMAL(10, 2) NOT NULL,
            billing_interval VARCHAR(20) DEFAULT 'monthly',

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_pricing_tiers_plan ON pricing_tiers(plan_id);
    """)

    # =========================================================================
    # 3. Create subscriptions table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            company_id UUID NOT NULL,
            plan_id UUID NOT NULL REFERENCES subscription_plans(id),

            -- Status
            status VARCHAR(30) DEFAULT 'trialing',
            billing_interval VARCHAR(20) DEFAULT 'monthly',

            -- Dates
            trial_start TIMESTAMP WITH TIME ZONE,
            trial_end TIMESTAMP WITH TIME ZONE,
            current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
            cancelled_at TIMESTAMP WITH TIME ZONE,
            cancel_at_period_end BOOLEAN DEFAULT FALSE,

            -- Pricing Snapshot
            base_price DECIMAL(12, 2) NOT NULL,
            per_employee_price DECIMAL(10, 2) NOT NULL,
            employee_count INTEGER DEFAULT 1,
            calculated_amount DECIMAL(12, 2) NOT NULL,
            discount_amount DECIMAL(12, 2) DEFAULT 0,
            tax_amount DECIMAL(12, 2) DEFAULT 0,
            total_amount DECIMAL(12, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'INR',

            -- Custom Limits
            custom_limits JSONB DEFAULT '{}',

            -- Payment
            payment_method VARCHAR(30),
            razorpay_subscription_id VARCHAR(100),
            razorpay_customer_id VARCHAR(100),

            -- Extra Data
            extra_data JSONB DEFAULT '{}',
            notes TEXT,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            created_by UUID
        );

        CREATE INDEX idx_subscriptions_company ON subscriptions(company_id);
        CREATE INDEX idx_subscriptions_plan ON subscriptions(plan_id);
        CREATE INDEX idx_subscriptions_status ON subscriptions(status);
        CREATE INDEX idx_subscriptions_razorpay ON subscriptions(razorpay_subscription_id);
    """)

    # =========================================================================
    # 4. Create billing_cycles table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS billing_cycles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,

            cycle_number INTEGER NOT NULL,
            period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            period_end TIMESTAMP WITH TIME ZONE NOT NULL,

            -- Snapshot
            employee_count INTEGER NOT NULL,
            base_amount DECIMAL(12, 2) NOT NULL,
            employee_amount DECIMAL(12, 2) NOT NULL,

            -- Usage
            api_calls_used INTEGER DEFAULT 0,
            ai_queries_used INTEGER DEFAULT 0,
            storage_used_gb DECIMAL(10, 2) DEFAULT 0,
            overage_amount DECIMAL(12, 2) DEFAULT 0,

            -- Totals
            subtotal DECIMAL(12, 2) NOT NULL,
            discount_amount DECIMAL(12, 2) DEFAULT 0,
            tax_amount DECIMAL(12, 2) DEFAULT 0,
            total_amount DECIMAL(12, 2) NOT NULL,

            -- Status
            is_invoiced BOOLEAN DEFAULT FALSE,
            invoice_id UUID,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_billing_cycles_subscription ON billing_cycles(subscription_id);
        CREATE INDEX idx_billing_cycles_period ON billing_cycles(period_start, period_end);
    """)

    # =========================================================================
    # 5. Create subscription_invoices table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscription_invoices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subscription_id UUID NOT NULL REFERENCES subscriptions(id),
            company_id UUID NOT NULL,

            -- Invoice ID
            invoice_number VARCHAR(50) UNIQUE NOT NULL,
            invoice_date DATE NOT NULL,
            due_date DATE NOT NULL,

            -- Period
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,

            -- Status
            status VARCHAR(30) DEFAULT 'pending',

            -- Line Items
            line_items JSONB DEFAULT '[]',

            -- Amounts
            subtotal DECIMAL(12, 2) NOT NULL,
            discount_amount DECIMAL(12, 2) DEFAULT 0,
            discount_description VARCHAR(200),

            -- GST
            taxable_amount DECIMAL(12, 2) NOT NULL,
            cgst_rate DECIMAL(5, 2) DEFAULT 9,
            cgst_amount DECIMAL(12, 2) DEFAULT 0,
            sgst_rate DECIMAL(5, 2) DEFAULT 9,
            sgst_amount DECIMAL(12, 2) DEFAULT 0,
            igst_rate DECIMAL(5, 2) DEFAULT 18,
            igst_amount DECIMAL(12, 2) DEFAULT 0,
            total_tax DECIMAL(12, 2) DEFAULT 0,

            -- Total
            total_amount DECIMAL(12, 2) NOT NULL,
            amount_paid DECIMAL(12, 2) DEFAULT 0,
            amount_due DECIMAL(12, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'INR',

            -- Customer Details
            customer_name VARCHAR(200) NOT NULL,
            customer_email VARCHAR(200),
            customer_gstin VARCHAR(20),
            customer_address TEXT,
            customer_state_code VARCHAR(5),

            -- Seller
            seller_gstin VARCHAR(20),
            place_of_supply VARCHAR(100),

            -- Payment
            payment_link VARCHAR(500),
            razorpay_invoice_id VARCHAR(100),

            -- PDF
            pdf_url VARCHAR(500),

            -- Notes
            notes TEXT,
            internal_notes TEXT,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            paid_at TIMESTAMP WITH TIME ZONE
        );

        CREATE INDEX idx_subscription_invoices_subscription ON subscription_invoices(subscription_id);
        CREATE INDEX idx_subscription_invoices_company ON subscription_invoices(company_id);
        CREATE INDEX idx_subscription_invoices_number ON subscription_invoices(invoice_number);
        CREATE INDEX idx_subscription_invoices_status ON subscription_invoices(status);
        CREATE INDEX idx_subscription_invoices_date ON subscription_invoices(invoice_date);
    """)

    # =========================================================================
    # 6. Create subscription_payments table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscription_payments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            invoice_id UUID NOT NULL REFERENCES subscription_invoices(id),
            company_id UUID NOT NULL,

            -- Payment Details
            payment_number VARCHAR(50) UNIQUE NOT NULL,
            payment_date TIMESTAMP WITH TIME ZONE NOT NULL,
            amount DECIMAL(12, 2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'INR',

            -- Method
            payment_method VARCHAR(30) NOT NULL,
            payment_gateway VARCHAR(30),

            -- Gateway Details
            gateway_payment_id VARCHAR(100),
            gateway_order_id VARCHAR(100),
            gateway_signature VARCHAR(200),

            -- Bank Transfer
            bank_reference VARCHAR(100),
            bank_name VARCHAR(100),

            -- UPI
            upi_transaction_id VARCHAR(100),
            upi_vpa VARCHAR(100),

            -- Status
            status VARCHAR(30) DEFAULT 'pending',
            failure_reason TEXT,

            -- Refund
            refund_amount DECIMAL(12, 2) DEFAULT 0,
            refund_reason TEXT,
            refunded_at TIMESTAMP WITH TIME ZONE,

            -- Extra Data
            gateway_response JSONB DEFAULT '{}',
            extra_data JSONB DEFAULT '{}',

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_subscription_payments_invoice ON subscription_payments(invoice_id);
        CREATE INDEX idx_subscription_payments_company ON subscription_payments(company_id);
        CREATE INDEX idx_subscription_payments_gateway ON subscription_payments(gateway_payment_id);
        CREATE INDEX idx_subscription_payments_status ON subscription_payments(status);
    """)

    # =========================================================================
    # 7. Create usage_meters table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS usage_meters (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
            company_id UUID NOT NULL,

            -- Usage Type
            usage_type VARCHAR(30) NOT NULL,

            -- Period
            period_start TIMESTAMP WITH TIME ZONE NOT NULL,
            period_end TIMESTAMP WITH TIME ZONE NOT NULL,

            -- Metrics
            quantity_used DECIMAL(12, 2) NOT NULL DEFAULT 0,
            quantity_limit DECIMAL(12, 2),
            quantity_remaining DECIMAL(12, 2),

            -- Overage
            overage_quantity DECIMAL(12, 2) DEFAULT 0,
            overage_rate DECIMAL(10, 4) DEFAULT 0,
            overage_amount DECIMAL(12, 2) DEFAULT 0,

            -- Daily
            daily_usage JSONB DEFAULT '{}',

            -- Alerts
            alert_threshold_percent INTEGER DEFAULT 80,
            alert_sent_at TIMESTAMP WITH TIME ZONE,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_usage_meters_subscription ON usage_meters(subscription_id);
        CREATE INDEX idx_usage_meters_company ON usage_meters(company_id);
        CREATE INDEX idx_usage_meters_type ON usage_meters(usage_type);
        CREATE INDEX idx_usage_meters_period ON usage_meters(period_start, period_end);
    """)

    # =========================================================================
    # 8. Create discounts table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,

            -- Type
            discount_type VARCHAR(20) NOT NULL,
            discount_value DECIMAL(12, 2) NOT NULL,
            max_discount_amount DECIMAL(12, 2),

            -- Applicability
            applicable_plans TEXT[] DEFAULT '{}',
            applicable_intervals TEXT[] DEFAULT '{}',
            min_employees INTEGER,
            min_amount DECIMAL(12, 2),

            -- Validity
            valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
            valid_until TIMESTAMP WITH TIME ZONE,
            max_redemptions INTEGER,
            redemption_count INTEGER DEFAULT 0,
            max_per_customer INTEGER DEFAULT 1,

            -- Status
            is_active BOOLEAN DEFAULT TRUE,
            is_first_time_only BOOLEAN DEFAULT FALSE,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            created_by UUID
        );

        CREATE INDEX idx_discounts_code ON discounts(code);
        CREATE INDEX idx_discounts_active ON discounts(is_active);
        CREATE INDEX idx_discounts_validity ON discounts(valid_from, valid_until);
    """)

    # =========================================================================
    # 9. Create subscription_discounts table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscription_discounts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
            discount_id UUID REFERENCES discounts(id),

            discount_code VARCHAR(50) NOT NULL,
            discount_type VARCHAR(20) NOT NULL,
            discount_value DECIMAL(12, 2) NOT NULL,
            calculated_discount DECIMAL(12, 2) NOT NULL,

            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            valid_until TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE
        );

        CREATE INDEX idx_subscription_discounts_subscription ON subscription_discounts(subscription_id);
        CREATE INDEX idx_subscription_discounts_discount ON subscription_discounts(discount_id);
    """)

    # =========================================================================
    # 10. Create subscription_audit_logs table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS subscription_audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subscription_id UUID NOT NULL,
            company_id UUID NOT NULL,

            action VARCHAR(50) NOT NULL,
            previous_state JSONB DEFAULT '{}',
            new_state JSONB DEFAULT '{}',
            change_reason TEXT,

            performed_by UUID,
            performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            ip_address VARCHAR(50),
            user_agent VARCHAR(500)
        );

        CREATE INDEX idx_subscription_audit_logs_subscription ON subscription_audit_logs(subscription_id);
        CREATE INDEX idx_subscription_audit_logs_company ON subscription_audit_logs(company_id);
        CREATE INDEX idx_subscription_audit_logs_action ON subscription_audit_logs(action);
        CREATE INDEX idx_subscription_audit_logs_performed ON subscription_audit_logs(performed_at DESC);
    """)

    # =========================================================================
    # 11. Create update triggers
    # =========================================================================
    op.execute("""
        CREATE TRIGGER trg_subscription_plans_update
        BEFORE UPDATE ON subscription_plans
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_subscriptions_update
        BEFORE UPDATE ON subscriptions
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_subscription_invoices_update
        BEFORE UPDATE ON subscription_invoices
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_subscription_payments_update
        BEFORE UPDATE ON subscription_payments
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_usage_meters_update
        BEFORE UPDATE ON usage_meters
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_discounts_update
        BEFORE UPDATE ON discounts
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();
    """)

    # =========================================================================
    # 12. Seed default subscription plans
    # =========================================================================
    op.execute("""
        INSERT INTO subscription_plans (code, name, description, plan_type,
            base_price_monthly, per_employee_monthly, base_price_annual, per_employee_annual,
            max_employees, max_users, storage_gb, api_calls_monthly, ai_queries_monthly,
            trial_days, is_active, is_public, display_order, highlight_text,
            features, modules_enabled)
        VALUES
        -- Free Plan
        ('PLAN-FREE', 'Free', 'Get started with basic features', 'free',
         0, 0, 0, 0,
         5, 2, 1, 1000, 10,
         0, TRUE, TRUE, 1, NULL,
         '{"hrms": true, "payroll": false, "crm": false, "projects": false}',
         ARRAY['hrms']),

        -- Starter Plan
        ('PLAN-STARTER', 'Starter', 'Perfect for small businesses', 'starter',
         999, 199, 9990, 1990,
         50, 10, 10, 10000, 100,
         14, TRUE, TRUE, 2, NULL,
         '{"hrms": true, "payroll": true, "crm": false, "projects": true, "attendance": true}',
         ARRAY['hrms', 'payroll', 'projects', 'attendance']),

        -- Professional Plan
        ('PLAN-PRO', 'Professional', 'Complete solution for growing companies', 'professional',
         2999, 299, 29990, 2490,
         200, 50, 50, 50000, 500,
         14, TRUE, TRUE, 3, 'Most Popular',
         '{"hrms": true, "payroll": true, "crm": true, "projects": true, "attendance": true, "ai": true}',
         ARRAY['hrms', 'payroll', 'crm', 'projects', 'attendance', 'ai']),

        -- Enterprise Plan
        ('PLAN-ENTERPRISE', 'Enterprise', 'Full-featured enterprise solution', 'enterprise',
         9999, 399, 99990, 3490,
         NULL, NULL, 500, 500000, 5000,
         30, TRUE, TRUE, 4, NULL,
         '{"hrms": true, "payroll": true, "crm": true, "projects": true, "attendance": true, "ai": true, "manufacturing": true, "supply_chain": true}',
         ARRAY['hrms', 'payroll', 'crm', 'projects', 'attendance', 'ai', 'manufacturing', 'supply_chain'])

        ON CONFLICT (code) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            base_price_monthly = EXCLUDED.base_price_monthly,
            per_employee_monthly = EXCLUDED.per_employee_monthly;
    """)

    # =========================================================================
    # 13. Seed pricing tiers for Professional plan
    # =========================================================================
    op.execute("""
        INSERT INTO pricing_tiers (plan_id, min_employees, max_employees, price_per_employee, billing_interval)
        SELECT id, 1, 50, 299, 'monthly' FROM subscription_plans WHERE code = 'PLAN-PRO'
        UNION ALL
        SELECT id, 51, 100, 249, 'monthly' FROM subscription_plans WHERE code = 'PLAN-PRO'
        UNION ALL
        SELECT id, 101, 200, 199, 'monthly' FROM subscription_plans WHERE code = 'PLAN-PRO';
    """)

    # =========================================================================
    # 14. Seed sample discounts
    # =========================================================================
    op.execute("""
        INSERT INTO discounts (code, name, description, discount_type, discount_value,
            valid_from, valid_until, max_redemptions, is_active)
        VALUES
        ('WELCOME20', 'Welcome Discount', '20% off for new customers', 'percentage', 20,
         NOW(), NOW() + INTERVAL '90 days', 1000, TRUE),
        ('ANNUAL30', 'Annual Plan Discount', '30% off on annual billing', 'percentage', 30,
         NOW(), NOW() + INTERVAL '1 year', NULL, TRUE),
        ('STARTUP50', 'Startup Special', '₹5000 off for startups', 'fixed_amount', 5000,
         NOW(), NOW() + INTERVAL '180 days', 500, TRUE)
        ON CONFLICT (code) DO NOTHING;
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_discounts_update ON discounts;")
    op.execute("DROP TRIGGER IF EXISTS trg_usage_meters_update ON usage_meters;")
    op.execute("DROP TRIGGER IF EXISTS trg_subscription_payments_update ON subscription_payments;")
    op.execute("DROP TRIGGER IF EXISTS trg_subscription_invoices_update ON subscription_invoices;")
    op.execute("DROP TRIGGER IF EXISTS trg_subscriptions_update ON subscriptions;")
    op.execute("DROP TRIGGER IF EXISTS trg_subscription_plans_update ON subscription_plans;")

    # Drop tables in reverse order
    op.execute("DROP TABLE IF EXISTS subscription_audit_logs;")
    op.execute("DROP TABLE IF EXISTS subscription_discounts;")
    op.execute("DROP TABLE IF EXISTS discounts;")
    op.execute("DROP TABLE IF EXISTS usage_meters;")
    op.execute("DROP TABLE IF EXISTS subscription_payments;")
    op.execute("DROP TABLE IF EXISTS subscription_invoices;")
    op.execute("DROP TABLE IF EXISTS billing_cycles;")
    op.execute("DROP TABLE IF EXISTS subscriptions;")
    op.execute("DROP TABLE IF EXISTS pricing_tiers;")
    op.execute("DROP TABLE IF EXISTS subscription_plans;")
