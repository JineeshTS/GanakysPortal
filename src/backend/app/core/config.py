"""
GanaPortal Configuration
Environment-based settings with Pydantic
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


# Weak/default secrets that should never be used in production
INSECURE_SECRETS = {
    "your-super-secret-key-change-in-production",
    "ganaportal-dev-secret-key-change-in-production-2026",
    "super-secret-key",
    "secret",
    "changeme",
    "change-me",
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "GanaPortal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://portal.ganakys.com"]

    # Database - SECURITY: Must be set via environment variable
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate that database URL is set and doesn't contain default credentials."""
        if not v:
            raise ValueError(
                "DATABASE_URL must be set via environment variable"
            )
        # Extract password from URL: scheme://user:password@host:port/db
        # URL format: postgresql+asyncpg://user:password@host:port/dbname
        try:
            # Find password between :// and @
            if "://" in v and "@" in v:
                auth_part = v.split("://")[1].split("@")[0]
                if ":" in auth_part:
                    password = auth_part.split(":", 1)[1]
                else:
                    password = ""
            else:
                password = ""
        except (IndexError, ValueError):
            password = ""

        # Check for known insecure default credentials in password only
        insecure_passwords = ["GanaPortal2026!", "password", "postgres", "changeme", "admin", "12345"]
        for insecure in insecure_passwords:
            if password and password.lower() == insecure.lower():
                raise ValueError(
                    f"DATABASE_URL contains insecure default password. "
                    f"Use a secure, randomly generated password."
                )

        # Check for minimum password length
        if password and len(password) < 16:
            raise ValueError(
                "DATABASE_URL password is too short. Use at least 16 characters."
            )

        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 1
    REDIS_CACHE_DB: int = 2

    # JWT Authentication
    # SECURITY: JWT_SECRET_KEY must be set via environment variable
    # Generate with: openssl rand -base64 64
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate that JWT secret is secure."""
        if not v:
            raise ValueError(
                "JWT_SECRET_KEY must be set. Generate with: openssl rand -base64 64"
            )
        if v.lower() in INSECURE_SECRETS or len(v) < 32:
            raise ValueError(
                "JWT_SECRET_KEY is insecure. Use a cryptographically random secret "
                "of at least 32 characters. Generate with: openssl rand -base64 64"
            )
        return v

    # AI Providers (Fallback Chain)
    CLAUDE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None

    # AI Models
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OPENAI_MODEL: str = "gpt-4-turbo"
    TOGETHER_MODEL: str = "meta-llama/Llama-3-70b-chat-hf"

    # AI Confidence Thresholds
    AI_AUTO_EXECUTE_THRESHOLD: float = 0.95
    AI_QUEUE_REVIEW_THRESHOLD: float = 0.70

    # File Storage
    FILE_STORAGE_PATH: str = "/var/data/ganaportal/files"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "xlsx", "csv", "doc", "docx"]

    # Email (SMTP - Hostinger)
    SMTP_HOST: str = "smtp.hostinger.com"
    SMTP_PORT: int = 465
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_SSL: bool = True
    SMTP_USE_TLS: bool = False
    EMAIL_FROM: str = "noreply@ganakys.com"
    EMAIL_FROM_NAME: str = "GanaPortal"

    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    FRONTEND_URL: str = "https://portal.ganakys.com"

    # SMS (MSG91)
    MSG91_AUTH_KEY: Optional[str] = None
    MSG91_SENDER_ID: str = "GANAK"

    # India Compliance
    COMPANY_STATE: str = "Karnataka"
    FINANCIAL_YEAR_START_MONTH: int = 4  # April
    PF_CONTRIBUTION_RATE: float = 0.12  # 12%
    ESI_EMPLOYEE_RATE: float = 0.0075  # 0.75%
    ESI_EMPLOYER_RATE: float = 0.0325  # 3.25%
    ESI_WAGE_LIMIT: int = 21000
    EPS_WAGE_LIMIT: int = 15000
    EPS_RATE: float = 0.0833  # 8.33%
    EPS_MAX_CONTRIBUTION: int = 1250

    # GST
    DEFAULT_GST_RATE: float = 0.18  # 18%
    CGST_RATE: float = 0.09  # 9%
    SGST_RATE: float = 0.09  # 9%

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/4"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
