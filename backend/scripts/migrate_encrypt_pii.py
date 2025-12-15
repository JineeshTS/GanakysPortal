#!/usr/bin/env python3
"""
Data Migration Script: Encrypt existing PII data.

This script encrypts existing unencrypted PII data in the database.
It should be run AFTER the Alembic migration that expands column sizes.

WBS Reference: FIX-WBS Task 2.1.1.7

Usage:
    python scripts/migrate_encrypt_pii.py [--dry-run]

Options:
    --dry-run    Preview changes without writing to database
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.security import encrypt_sensitive_data, decrypt_sensitive_data
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_encrypted(value: str) -> bool:
    """
    Check if a value appears to be already encrypted.

    Fernet encrypted values are base64 encoded and start with 'gAAAAA'.
    """
    if not value:
        return False
    try:
        # Try to decrypt - if it works, it's encrypted
        decrypt_sensitive_data(value)
        return True
    except Exception:
        return False


async def migrate_employee_identity(db: AsyncSession, dry_run: bool = False) -> dict:
    """Migrate EmployeeIdentity PII fields."""
    from app.models.employee import EmployeeIdentity

    stats = {'processed': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    result = await db.execute(select(EmployeeIdentity))
    records = result.scalars().all()

    for record in records:
        stats['processed'] += 1
        changes = {}

        # Check and encrypt PAN
        if record.pan_number and not is_encrypted(record.pan_number):
            changes['pan_number'] = encrypt_sensitive_data(record.pan_number)

        # Check and encrypt Aadhaar
        if record.aadhaar_number and not is_encrypted(record.aadhaar_number):
            changes['aadhaar_number'] = encrypt_sensitive_data(record.aadhaar_number)

        # Check and encrypt Passport
        if record.passport_number and not is_encrypted(record.passport_number):
            changes['passport_number'] = encrypt_sensitive_data(record.passport_number)

        if changes:
            if not dry_run:
                for field, value in changes.items():
                    setattr(record, field, value)
            stats['encrypted'] += 1
            logger.info(f"EmployeeIdentity {record.id}: encrypted {list(changes.keys())}")
        else:
            stats['skipped'] += 1

    return stats


async def migrate_employee_bank(db: AsyncSession, dry_run: bool = False) -> dict:
    """Migrate EmployeeBank PII fields."""
    from app.models.employee import EmployeeBank

    stats = {'processed': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    result = await db.execute(select(EmployeeBank))
    records = result.scalars().all()

    for record in records:
        stats['processed'] += 1

        if record.account_number and not is_encrypted(record.account_number):
            if not dry_run:
                record.account_number = encrypt_sensitive_data(record.account_number)
            stats['encrypted'] += 1
            logger.info(f"EmployeeBank {record.id}: encrypted account_number")
        else:
            stats['skipped'] += 1

    return stats


async def migrate_vendor(db: AsyncSession, dry_run: bool = False) -> dict:
    """Migrate Vendor PII fields."""
    from app.models.vendor import Vendor

    stats = {'processed': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    result = await db.execute(select(Vendor))
    records = result.scalars().all()

    for record in records:
        stats['processed'] += 1

        if record.pan and not is_encrypted(record.pan):
            if not dry_run:
                record.pan = encrypt_sensitive_data(record.pan)
            stats['encrypted'] += 1
            logger.info(f"Vendor {record.id}: encrypted pan")
        else:
            stats['skipped'] += 1

    return stats


async def migrate_customer(db: AsyncSession, dry_run: bool = False) -> dict:
    """Migrate Customer PII fields."""
    from app.models.customer import Customer

    stats = {'processed': 0, 'encrypted': 0, 'skipped': 0, 'errors': 0}

    result = await db.execute(select(Customer))
    records = result.scalars().all()

    for record in records:
        stats['processed'] += 1

        if record.pan and not is_encrypted(record.pan):
            if not dry_run:
                record.pan = encrypt_sensitive_data(record.pan)
            stats['encrypted'] += 1
            logger.info(f"Customer {record.id}: encrypted pan")
        else:
            stats['skipped'] += 1

    return stats


async def main(dry_run: bool = False):
    """Run the PII encryption migration."""
    logger.info("=" * 60)
    logger.info("PII Encryption Migration")
    logger.info(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    async with async_session_maker() as db:
        try:
            # Migrate each table
            results = {}

            logger.info("\nMigrating EmployeeIdentity...")
            results['EmployeeIdentity'] = await migrate_employee_identity(db, dry_run)

            logger.info("\nMigrating EmployeeBank...")
            results['EmployeeBank'] = await migrate_employee_bank(db, dry_run)

            logger.info("\nMigrating Vendor...")
            results['Vendor'] = await migrate_vendor(db, dry_run)

            logger.info("\nMigrating Customer...")
            results['Customer'] = await migrate_customer(db, dry_run)

            # Commit if not dry run
            if not dry_run:
                await db.commit()
                logger.info("\nChanges committed to database.")
            else:
                await db.rollback()
                logger.info("\nDry run complete. No changes made.")

            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("MIGRATION SUMMARY")
            logger.info("=" * 60)
            for table, stats in results.items():
                logger.info(f"\n{table}:")
                logger.info(f"  Processed: {stats['processed']}")
                logger.info(f"  Encrypted: {stats['encrypted']}")
                logger.info(f"  Skipped (already encrypted): {stats['skipped']}")
                logger.info(f"  Errors: {stats['errors']}")

            total_encrypted = sum(s['encrypted'] for s in results.values())
            logger.info(f"\nTotal records encrypted: {total_encrypted}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt existing PII data")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to database"
    )
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run))
