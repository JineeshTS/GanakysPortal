"""
Timezone-aware datetime utilities.

Python 3.12 deprecated utc_now() in favor of timezone-aware datetimes.
This module provides utilities to replace deprecated utc_now() usage.

Usage:
    # Instead of: utc_now()
    # Use: utc_now()

    # For SQLAlchemy column defaults:
    # Instead of: default=datetime.utcnow
    # Use: default=utc_now
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Return current UTC time as a timezone-aware datetime.

    This is the recommended replacement for utc_now() which
    was deprecated in Python 3.12.

    Returns:
        datetime: Current UTC time with timezone info.
    """
    return datetime.now(timezone.utc)


# Alias for SQLAlchemy column defaults (callable)
def get_utc_now():
    """Alias for utc_now(), useful for SQLAlchemy defaults."""
    return utc_now()


# Constants
UTC = timezone.utc
