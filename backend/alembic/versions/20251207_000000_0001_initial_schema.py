"""Initial schema with users, employees, departments, designations

Revision ID: 0001
Revises:
Create Date: 2025-12-07

WBS Reference: Tasks 3.1.1.1.1, 3.2.1.1.1 - 3.2.1.1.7
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'hr', 'accountant', 'employee', 'external_ca')")
    op.execute("CREATE TYPE gender AS ENUM ('male', 'female', 'other')")
    op.execute("CREATE TYPE bloodgroup AS ENUM ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')")
    op.execute("CREATE TYPE maritalstatus AS ENUM ('single', 'married', 'divorced', 'widowed')")
    op.execute("CREATE TYPE onboardingstatus AS ENUM ('pending', 'in_progress', 'completed', 'approved')")
    op.execute("CREATE TYPE employmenttype AS ENUM ('full_time', 'part_time', 'contract', 'intern', 'consultant')")
    op.execute("CREATE TYPE employmentstatus AS ENUM ('active', 'on_notice', 'relieved', 'terminated', 'absconding')")

    # Users table (WBS 3.1.1.1.1)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'hr', 'accountant', 'employee', 'external_ca', name='userrole', create_type=False), nullable=False, server_default='employee'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Departments table (WBS 3.2.1.1.6)
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('head_employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Designations table (WBS 3.2.1.1.7)
    op.create_table(
        'designations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Employees table (WBS 3.2.1.1.1)
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('employee_code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', postgresql.ENUM('male', 'female', 'other', name='gender', create_type=False), nullable=True),
        sa.Column('blood_group', postgresql.ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', name='bloodgroup', create_type=False), nullable=True),
        sa.Column('marital_status', postgresql.ENUM('single', 'married', 'divorced', 'widowed', name='maritalstatus', create_type=False), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=False, server_default='Indian'),
        sa.Column('profile_photo_path', sa.String(500), nullable=True),
        sa.Column('onboarding_status', postgresql.ENUM('pending', 'in_progress', 'completed', 'approved', name='onboardingstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Add foreign key for department head after employees table exists
    op.create_foreign_key(
        'fk_departments_head_employee',
        'departments', 'employees',
        ['head_employee_id'], ['id'],
        ondelete='SET NULL'
    )

    # Employee contacts table (WBS 3.2.1.1.2)
    op.create_table(
        'employee_contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('personal_email', sa.String(255), nullable=True),
        sa.Column('personal_phone', sa.String(20), nullable=True),
        sa.Column('emergency_contact_name', sa.String(100), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(20), nullable=True),
        sa.Column('emergency_contact_relation', sa.String(50), nullable=True),
        sa.Column('current_address_line1', sa.String(255), nullable=True),
        sa.Column('current_address_line2', sa.String(255), nullable=True),
        sa.Column('current_city', sa.String(100), nullable=True),
        sa.Column('current_state', sa.String(100), nullable=True),
        sa.Column('current_pincode', sa.String(10), nullable=True),
        sa.Column('current_country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('is_permanent_same_as_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('permanent_address_line1', sa.String(255), nullable=True),
        sa.Column('permanent_address_line2', sa.String(255), nullable=True),
        sa.Column('permanent_city', sa.String(100), nullable=True),
        sa.Column('permanent_state', sa.String(100), nullable=True),
        sa.Column('permanent_pincode', sa.String(10), nullable=True),
        sa.Column('permanent_country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Employee identities table (WBS 3.2.1.1.3)
    op.create_table(
        'employee_identities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('pan_number', sa.String(500), nullable=True),  # Encrypted
        sa.Column('aadhaar_number', sa.String(500), nullable=True),  # Encrypted
        sa.Column('passport_number', sa.String(500), nullable=True),  # Encrypted
        sa.Column('passport_expiry', sa.Date(), nullable=True),
        sa.Column('driving_license', sa.String(50), nullable=True),
        sa.Column('voter_id', sa.String(50), nullable=True),
        sa.Column('uan_number', sa.String(20), nullable=True),
        sa.Column('esi_number', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Employee bank accounts table (WBS 3.2.1.1.4)
    op.create_table(
        'employee_bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('bank_name', sa.String(100), nullable=False),
        sa.Column('branch_name', sa.String(100), nullable=True),
        sa.Column('account_number', sa.String(500), nullable=False),  # Encrypted
        sa.Column('ifsc_code', sa.String(20), nullable=False),
        sa.Column('account_type', sa.String(20), nullable=False, server_default='savings'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Employee employment table (WBS 3.2.1.1.5)
    op.create_table(
        'employee_employments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('designation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('designations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reporting_manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True),
        sa.Column('employment_type', postgresql.ENUM('full_time', 'part_time', 'contract', 'intern', 'consultant', name='employmenttype', create_type=False), nullable=False, server_default='full_time'),
        sa.Column('date_of_joining', sa.Date(), nullable=True),
        sa.Column('probation_end_date', sa.Date(), nullable=True),
        sa.Column('confirmation_date', sa.Date(), nullable=True),
        sa.Column('date_of_exit', sa.Date(), nullable=True),
        sa.Column('exit_reason', sa.Text(), nullable=True),
        sa.Column('notice_period_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('current_status', postgresql.ENUM('active', 'on_notice', 'relieved', 'terminated', 'absconding', name='employmentstatus', create_type=False), nullable=False, server_default='active'),
        sa.Column('work_location', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create indexes
    op.create_index('ix_employees_user_id', 'employees', ['user_id'])
    op.create_index('ix_employee_contacts_employee_id', 'employee_contacts', ['employee_id'])
    op.create_index('ix_employee_identities_employee_id', 'employee_identities', ['employee_id'])
    op.create_index('ix_employee_bank_accounts_employee_id', 'employee_bank_accounts', ['employee_id'])
    op.create_index('ix_employee_employments_employee_id', 'employee_employments', ['employee_id'])
    op.create_index('ix_employee_employments_department_id', 'employee_employments', ['department_id'])

    # Seed default departments (WBS 3.2.1.1.6)
    op.execute("""
        INSERT INTO departments (id, name, code, description) VALUES
        (gen_random_uuid(), 'Engineering', 'ENG', 'Software development and technical team'),
        (gen_random_uuid(), 'Human Resources', 'HR', 'HR and people operations'),
        (gen_random_uuid(), 'Finance', 'FIN', 'Finance and accounting'),
        (gen_random_uuid(), 'Operations', 'OPS', 'Operations and administration')
    """)

    # Seed default designations (WBS 3.2.1.1.7)
    op.execute("""
        INSERT INTO designations (id, name, code, level) VALUES
        (gen_random_uuid(), 'Founder & CEO', 'CEO', 10),
        (gen_random_uuid(), 'Director', 'DIR', 9),
        (gen_random_uuid(), 'Senior Manager', 'SR-MGR', 7),
        (gen_random_uuid(), 'Manager', 'MGR', 6),
        (gen_random_uuid(), 'Team Lead', 'TL', 5),
        (gen_random_uuid(), 'Senior Software Engineer', 'SR-SWE', 4),
        (gen_random_uuid(), 'Software Engineer', 'SWE', 3),
        (gen_random_uuid(), 'Junior Software Engineer', 'JR-SWE', 2),
        (gen_random_uuid(), 'Intern', 'INT', 1)
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('employee_employments')
    op.drop_table('employee_bank_accounts')
    op.drop_table('employee_identities')
    op.drop_table('employee_contacts')

    # Drop foreign key before dropping employees
    op.drop_constraint('fk_departments_head_employee', 'departments', type_='foreignkey')

    op.drop_table('employees')
    op.drop_table('designations')
    op.drop_table('departments')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS employmentstatus')
    op.execute('DROP TYPE IF EXISTS employmenttype')
    op.execute('DROP TYPE IF EXISTS onboardingstatus')
    op.execute('DROP TYPE IF EXISTS maritalstatus')
    op.execute('DROP TYPE IF EXISTS bloodgroup')
    op.execute('DROP TYPE IF EXISTS gender')
    op.execute('DROP TYPE IF EXISTS userrole')
