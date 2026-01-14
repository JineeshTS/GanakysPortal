"""
GanaPortal Configuration
Environment-based settings with Pydantic
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ganaportal_user:GanaPortal2026!@localhost:5432/ganaportal"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 1
    REDIS_CACHE_DB: int = 2

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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

    # Email (AWS SES / SendGrid)
    EMAIL_PROVIDER: str = "ses"  # ses, sendgrid
    AWS_SES_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@ganakys.com"

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
