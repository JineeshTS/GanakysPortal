"""
Application configuration settings.
"""
import logging
import warnings
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default values that indicate unconfigured secrets
_INSECURE_DEFAULTS = [
    "your-super-secret-key-change-in-production",
    "your-32-byte-encryption-key-here",
]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow unknown env vars for flexibility
    )

    # Application
    APP_NAME: str = "GanaPortal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        description="Secret key for JWT encoding",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Password policy
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ganaportal",
        description="PostgreSQL connection URL",
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # File Storage
    UPLOAD_DIR: str = "/var/data/gana-portal"
    EDMS_UPLOAD_DIR: str = "/var/data/gana-portal/edms"
    EMPLOYEE_DOCS_DIR: str = "/var/data/gana-portal/employee-docs"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "doc", "docx", "xls", "xlsx", "csv",
        "jpg", "jpeg", "png", "gif", "webp",
        "txt", "rtf", "odt", "ods",
    ]

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@ganakys.com"
    SMTP_FROM_NAME: str = "GanaPortal"
    SMTP_TLS: bool = True

    # Claude AI
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    AI_MAX_TOKENS: int = 4096
    AI_RATE_LIMIT_PER_MINUTE: int = 60

    # Company defaults (for initial setup)
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"
    DEFAULT_CURRENCY: str = "INR"
    DEFAULT_DATE_FORMAT: str = "DD/MM/YYYY"

    # Encryption key for sensitive data (PAN, Aadhaar, Bank Account)
    ENCRYPTION_KEY: str = Field(
        default="your-32-byte-encryption-key-here",
        description="AES-256 encryption key for sensitive data",
    )

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        """
        Validate security-critical settings.

        - In production: Raise error if default secrets are used
        - In development: Log warning if default secrets are used
        """
        insecure_fields = []

        if self.SECRET_KEY in _INSECURE_DEFAULTS:
            insecure_fields.append("SECRET_KEY")

        if self.ENCRYPTION_KEY in _INSECURE_DEFAULTS:
            insecure_fields.append("ENCRYPTION_KEY")

        if insecure_fields:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    f"CRITICAL: Insecure default values detected for: {', '.join(insecure_fields)}. "
                    f"These MUST be changed in production. Generate secure keys with: "
                    f"python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            else:
                # Development/staging: warn but allow
                warnings.warn(
                    f"WARNING: Using default values for: {', '.join(insecure_fields)}. "
                    f"This is acceptable for development but MUST be changed for production.",
                    UserWarning,
                    stacklevel=2,
                )

        return self

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT in ("development", "dev", "local")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
