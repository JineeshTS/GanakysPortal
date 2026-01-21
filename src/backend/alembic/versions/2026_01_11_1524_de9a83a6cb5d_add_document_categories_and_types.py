"""add_document_categories_and_types

Revision ID: de9a83a6cb5d
Revises: fe952d6e0eac
Create Date: 2026-01-11 15:24:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'de9a83a6cb5d'
down_revision: Union[str, None] = 'fe952d6e0eac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create document_categories table
    op.execute("""
        CREATE TABLE IF NOT EXISTS document_categories (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES companies(id),
            code VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            color VARCHAR(20) DEFAULT '#3B82F6',
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            is_system BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(company_id, code)
        );
    """)

    # Create document_types table
    op.execute("""
        CREATE TABLE IF NOT EXISTS document_types (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES companies(id),
            category_id UUID REFERENCES document_categories(id),
            code VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            required_fields JSONB,
            sort_order INTEGER DEFAULT 0,
            is_system BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(company_id, code)
        );
    """)

    # Add category_id to folders table (if folders table exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'folders') THEN
                ALTER TABLE folders ADD COLUMN IF NOT EXISTS category_id UUID REFERENCES document_categories(id);
            END IF;
        END $$;
    """)

    # Seed default categories (system-wide, company_id = NULL)
    op.execute("""
        INSERT INTO document_categories (code, name, description, color, icon, sort_order, is_system) VALUES
        ('hr', 'HR', 'Human Resources documents', '#8B5CF6', 'users', 1, TRUE),
        ('finance', 'Finance', 'Financial documents', '#10B981', 'dollar-sign', 2, TRUE),
        ('legal', 'Legal', 'Legal documents and contracts', '#F59E0B', 'scale', 3, TRUE),
        ('compliance', 'Compliance', 'Compliance and regulatory documents', '#EF4444', 'shield', 4, TRUE),
        ('payroll', 'Payroll', 'Payroll and salary documents', '#06B6D4', 'credit-card', 5, TRUE),
        ('employee', 'Employee', 'Employee personal documents', '#EC4899', 'user', 6, TRUE),
        ('project', 'Project', 'Project related documents', '#6366F1', 'folder', 7, TRUE),
        ('general', 'General', 'General documents', '#6B7280', 'file', 8, TRUE)
        ON CONFLICT (company_id, code) DO NOTHING;
    """)

    # Seed default document types
    op.execute("""
        INSERT INTO document_types (category_id, code, name, description, sort_order, is_system)
        SELECT c.id, t.code, t.name, t.description, t.sort_order, TRUE
        FROM document_categories c
        CROSS JOIN (VALUES
            -- HR types
            ('hr', 'offer_letter', 'Offer Letter', 'Job offer letters', 1),
            ('hr', 'appointment_letter', 'Appointment Letter', 'Employment appointment letters', 2),
            ('hr', 'experience_letter', 'Experience Letter', 'Work experience certificates', 3),
            ('hr', 'relieving_letter', 'Relieving Letter', 'Employment relieving letters', 4),
            ('hr', 'warning_letter', 'Warning Letter', 'Disciplinary warning letters', 5),
            ('hr', 'termination_letter', 'Termination Letter', 'Employment termination letters', 6),
            -- Payroll types
            ('payroll', 'salary_slip', 'Salary Slip', 'Monthly salary slips', 1),
            ('payroll', 'form_16', 'Form 16', 'Annual tax Form 16', 2),
            ('payroll', 'bonus_letter', 'Bonus Letter', 'Bonus declaration letters', 3),
            ('payroll', 'increment_letter', 'Increment Letter', 'Salary increment letters', 4),
            -- Employee types
            ('employee', 'resume', 'Resume', 'Employee resume/CV', 1),
            ('employee', 'photo', 'Photo', 'Employee photograph', 2),
            ('employee', 'id_proof', 'ID Proof', 'Government ID proof', 3),
            ('employee', 'pan_card', 'PAN Card', 'PAN card copy', 4),
            ('employee', 'aadhaar', 'Aadhaar', 'Aadhaar card copy', 5),
            ('employee', 'passport', 'Passport', 'Passport copy', 6),
            ('employee', 'bank_details', 'Bank Details', 'Bank account details', 7),
            ('employee', 'educational_cert', 'Educational Certificate', 'Educational certificates', 8),
            -- Finance types
            ('finance', 'invoice', 'Invoice', 'Sales/Purchase invoices', 1),
            ('finance', 'receipt', 'Receipt', 'Payment receipts', 2),
            ('finance', 'purchase_order', 'Purchase Order', 'Purchase orders', 3),
            ('finance', 'quotation', 'Quotation', 'Price quotations', 4),
            ('finance', 'bank_statement', 'Bank Statement', 'Bank statements', 5),
            -- Legal types
            ('legal', 'contract', 'Contract', 'Business contracts', 1),
            ('legal', 'agreement', 'Agreement', 'Agreements', 2),
            ('legal', 'nda', 'NDA', 'Non-disclosure agreements', 3),
            ('legal', 'mou', 'MOU', 'Memorandum of understanding', 4),
            -- Compliance types
            ('compliance', 'gst_return', 'GST Return', 'GST return filings', 1),
            ('compliance', 'tds_return', 'TDS Return', 'TDS return filings', 2),
            ('compliance', 'pf_challan', 'PF Challan', 'PF payment challans', 3),
            ('compliance', 'esi_challan', 'ESI Challan', 'ESI payment challans', 4),
            -- General types
            ('general', 'report', 'Report', 'Reports and analytics', 1),
            ('general', 'presentation', 'Presentation', 'Presentations', 2),
            ('general', 'spreadsheet', 'Spreadsheet', 'Spreadsheets and data files', 3),
            ('general', 'other', 'Other', 'Other documents', 99)
        ) AS t(category_code, code, name, description, sort_order)
        WHERE c.code = t.category_code AND c.company_id IS NULL
        ON CONFLICT (company_id, code) DO NOTHING;
    """)

    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_categories_company ON document_categories(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_types_company ON document_types(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_doc_types_category ON document_types(category_id);")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'folders') THEN
                CREATE INDEX IF NOT EXISTS idx_folders_category ON folders(category_id);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'folders') THEN
                ALTER TABLE folders DROP COLUMN IF EXISTS category_id;
            END IF;
        END $$;
    """)
    op.execute("DROP TABLE IF EXISTS document_types;")
    op.execute("DROP TABLE IF EXISTS document_categories;")
