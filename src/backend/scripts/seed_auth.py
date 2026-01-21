#!/usr/bin/env python3
"""
Seed script for Authentication Module
Creates initial company and admin user for GanaPortal
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import bcrypt
from uuid import uuid4
from datetime import datetime

# Database URL - must be set via environment variable (no hardcoded fallback for security)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


async def seed_database():
    """Seed the database with initial data."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if company already exists
            result = await session.execute(text("SELECT COUNT(*) FROM companies"))
            count = result.scalar()

            if count > 0:
                print("✓ Company already exists, skipping company creation")
                # Get existing company ID
                result = await session.execute(text("SELECT id FROM companies LIMIT 1"))
                company_id = result.scalar()
            else:
                # Create company
                company_id = uuid4()
                await session.execute(text("""
                    INSERT INTO companies (
                        id, name, legal_name, cin, pan, tan, gstin,
                        address_line1, city, state, pincode, country,
                        phone, email, website, financial_year_start, currency,
                        created_at, updated_at
                    ) VALUES (
                        :id, :name, :legal_name, :cin, :pan, :tan, :gstin,
                        :address_line1, :city, :state, :pincode, :country,
                        :phone, :email, :website, :financial_year_start, :currency,
                        :created_at, :updated_at
                    )
                """), {
                    "id": company_id,
                    "name": "Ganakys Codilla Apps",
                    "legal_name": "Ganakys Codilla Apps (OPC) Private Limited",
                    "cin": "U72900KA2024OPC123456",
                    "pan": "AABCG1234A",
                    "tan": "BLRG12345A",
                    "gstin": "29AABCG1234A1Z5",
                    "address_line1": "Bangalore",
                    "city": "Bangalore",
                    "state": "Karnataka",
                    "pincode": "560001",
                    "country": "India",
                    "phone": "+91-80-12345678",
                    "email": "info@ganakys.com",
                    "website": "https://ganakys.com",
                    "financial_year_start": 4,
                    "currency": "INR",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                print(f"✓ Created company: Ganakys Codilla Apps (ID: {company_id})")

            # Check if admin user already exists
            result = await session.execute(text(
                "SELECT COUNT(*) FROM users WHERE email = 'admin@ganakys.com'"
            ))
            user_count = result.scalar()

            if user_count > 0:
                print("✓ Admin user already exists, skipping user creation")
            else:
                # Create admin user
                admin_id = uuid4()
                # SECURITY: Password must be set via environment variable
                admin_password = os.getenv("ADMIN_PASSWORD")
                if not admin_password:
                    # Generate a secure random password if not provided
                    import secrets
                    import string
                    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
                    admin_password = ''.join(secrets.choice(alphabet) for _ in range(16))
                    print(f"⚠️  IMPORTANT: Generated admin password: {admin_password}")
                    print("⚠️  Please change this password immediately after first login!")
                password_hash = get_password_hash(admin_password)

                await session.execute(text("""
                    INSERT INTO users (
                        id, email, password_hash, role, company_id,
                        is_active, is_verified, created_at, updated_at
                    ) VALUES (
                        :id, :email, :password_hash, :role, :company_id,
                        :is_active, :is_verified, :created_at, :updated_at
                    )
                """), {
                    "id": admin_id,
                    "email": "admin@ganakys.com",
                    "password_hash": password_hash,
                    "role": "admin",
                    "company_id": company_id,
                    "is_active": True,
                    "is_verified": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                print(f"✓ Created admin user: admin@ganakys.com (ID: {admin_id})")

            # Create additional test users
            test_users = [
                ("hr@ganakys.com", "hr", "Hr@2026"),
                ("accountant@ganakys.com", "accountant", "Account@2026"),
                ("employee@ganakys.com", "employee", "Employee@2026"),
            ]

            for email, role, password in test_users:
                result = await session.execute(text(
                    "SELECT COUNT(*) FROM users WHERE email = :email"
                ), {"email": email})
                if result.scalar() == 0:
                    user_id = uuid4()
                    await session.execute(text("""
                        INSERT INTO users (
                            id, email, password_hash, role, company_id,
                            is_active, is_verified, created_at, updated_at
                        ) VALUES (
                            :id, :email, :password_hash, :role, :company_id,
                            :is_active, :is_verified, :created_at, :updated_at
                        )
                    """), {
                        "id": user_id,
                        "email": email,
                        "password_hash": get_password_hash(password),
                        "role": role,
                        "company_id": company_id,
                        "is_active": True,
                        "is_verified": True,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    print(f"✓ Created {role} user: {email} (Password: {password})")
                else:
                    print(f"✓ User {email} already exists, skipping")

            await session.commit()
            print("\n✓ Database seeding completed successfully!")

            # Print summary
            print("\n" + "="*50)
            print("LOGIN CREDENTIALS")
            print("="*50)
            print("Admin:      admin@ganakys.com")
            print("            (password from ADMIN_PASSWORD env var or generated above)")
            print("HR:         hr@ganakys.com / Hr@2026")
            print("Accountant: accountant@ganakys.com / Account@2026")
            print("Employee:   employee@ganakys.com / Employee@2026")
            print("="*50)
            print("\n⚠️  WARNING: Test user passwords are hardcoded for demo only!")
            print("   Change these in production or use environment variables.")

        except Exception as e:
            print(f"✗ Error seeding database: {e}")
            await session.rollback()
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
