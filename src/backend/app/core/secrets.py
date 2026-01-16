"""
Secrets Management for GanaPortal
Secure handling of credentials and sensitive configuration
"""
import os
import secrets
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Centralized secrets management.

    Priority order for loading secrets:
    1. Environment variables (for production/container deployments)
    2. .env file (for development)
    3. Generated secure defaults (for local development only)

    IMPORTANT: Never commit actual secrets to version control.
    Use environment variables in production.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._secrets_cache = {}
        self._load_secrets()

    def _load_secrets(self):
        """Load all secrets from environment."""
        # These should ALWAYS come from environment in production
        self._secrets_cache = {
            'jwt_secret_key': self._get_required_secret('JWT_SECRET_KEY'),
            'database_password': self._get_secret_from_url('DATABASE_URL'),
            'encryption_key': self._get_required_secret('ENCRYPTION_KEY'),
            'smtp_password': os.environ.get('SMTP_PASSWORD'),
            'anthropic_api_key': os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY'),
            'openai_api_key': os.environ.get('OPENAI_API_KEY'),
            'gemini_api_key': os.environ.get('GEMINI_API_KEY'),
            'together_api_key': os.environ.get('TOGETHER_API_KEY'),
            'redis_password': os.environ.get('REDIS_PASSWORD'),
            'msg91_auth_key': os.environ.get('MSG91_AUTH_KEY'),
        }

    def _get_required_secret(self, key: str) -> str:
        """Get a required secret, generate secure default for development."""
        value = os.environ.get(key)

        if value:
            return value

        # In development, generate secure random value
        env = os.environ.get('ENVIRONMENT', 'development')
        if env == 'production':
            raise ValueError(f"Required secret {key} not set in production environment!")

        # Generate secure random key for development
        generated = secrets.token_hex(32)
        logger.warning(f"Generated temporary {key} for development. Set in environment for production.")
        return generated

    def _get_secret_from_url(self, url_key: str) -> Optional[str]:
        """Extract password from database URL."""
        url = os.environ.get(url_key, '')
        try:
            # Format: postgresql+asyncpg://user:password@host:port/database
            if '@' in url and ':' in url.split('@')[0]:
                credentials = url.split('@')[0].split('://')[-1]
                if ':' in credentials:
                    return credentials.split(':')[-1]
        except Exception:
            pass
        return None

    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key."""
        return self._secrets_cache['jwt_secret_key']

    @property
    def encryption_key(self) -> str:
        """Get encryption key for AES-256-GCM."""
        return self._secrets_cache['encryption_key']

    @property
    def database_password(self) -> Optional[str]:
        """Get database password."""
        return self._secrets_cache['database_password']

    @property
    def smtp_password(self) -> Optional[str]:
        """Get SMTP password."""
        return self._secrets_cache['smtp_password']

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """Get Anthropic API key."""
        return self._secrets_cache['anthropic_api_key']

    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self._secrets_cache['openai_api_key']

    @property
    def gemini_api_key(self) -> Optional[str]:
        """Get Google Gemini API key."""
        return self._secrets_cache['gemini_api_key']

    @property
    def together_api_key(self) -> Optional[str]:
        """Get Together AI API key."""
        return self._secrets_cache['together_api_key']

    @property
    def redis_password(self) -> Optional[str]:
        """Get Redis password."""
        return self._secrets_cache['redis_password']

    def get_secret(self, key: str) -> Optional[str]:
        """Get any secret by key."""
        return self._secrets_cache.get(key) or os.environ.get(key.upper())

    def mask_secret(self, value: str) -> str:
        """Mask a secret for logging (show first and last 4 chars)."""
        if not value or len(value) < 10:
            return '***'
        return f"{value[:4]}...{value[-4:]}"

    def validate_production_secrets(self) -> list[str]:
        """
        Validate that all required secrets are properly set for production.
        Returns list of missing/invalid secrets.
        """
        errors = []

        # Required secrets for production
        required = ['jwt_secret_key', 'encryption_key', 'database_password']

        for secret_name in required:
            value = self._secrets_cache.get(secret_name)
            if not value:
                errors.append(f"Missing required secret: {secret_name}")
            elif secret_name == 'jwt_secret_key' and len(value) < 32:
                errors.append("JWT secret key should be at least 32 characters")
            elif secret_name == 'encryption_key' and len(value) < 32:
                errors.append("Encryption key should be at least 32 characters")

        # Check for obviously insecure values
        insecure_patterns = ['secret', 'password', 'change', 'default', 'test', 'dev']
        for secret_name, value in self._secrets_cache.items():
            if value:
                lower_value = value.lower()
                for pattern in insecure_patterns:
                    if pattern in lower_value:
                        errors.append(f"Secret {secret_name} contains insecure pattern: {pattern}")
                        break

        return errors


@lru_cache
def get_secrets_manager() -> SecretsManager:
    """Get singleton secrets manager instance."""
    return SecretsManager()


# Singleton instance
secrets_manager = get_secrets_manager()
