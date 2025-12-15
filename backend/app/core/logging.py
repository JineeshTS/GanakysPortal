"""
Logging configuration for GanaPortal.
WBS Reference: Task 1.3.1.1 (Fix WBS)
"""
import logging
import sys
from typing import Optional

from app.core.config import settings


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds request ID to log records.

    This allows correlating log entries with specific HTTP requests.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to log record."""
        # Import here to avoid circular imports
        try:
            from app.core.middleware import get_request_id
            record.request_id = get_request_id() or "-"
        except ImportError:
            record.request_id = "-"
        return True


def setup_logging(
    log_level: Optional[str] = None,
    json_format: bool = False,
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format for structured logging

    Returns:
        Root logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = "DEBUG" if settings.DEBUG else "INFO"

    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter with request ID
    if json_format:
        # JSON format for production (easier to parse)
        format_str = (
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"request_id": "%(request_id)s", "logger": "%(name)s", '
            '"message": "%(message)s"}'
        )
    else:
        # Human-readable format for development
        format_str = (
            "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s:%(lineno)d | %(message)s"
        )

    formatter = logging.Formatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add request ID filter
    request_id_filter = RequestIDFilter()
    root_logger.addFilter(request_id_filter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_id_filter)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # SQLAlchemy logging - only show SQL in debug mode
    if settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on import
_root_logger = setup_logging()
