"""
Redis connection for caching and session management.
"""
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

# Redis client instance
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


class TokenBlacklist:
    """Manage blacklisted JWT tokens in Redis."""

    PREFIX = "token_blacklist:"

    @classmethod
    async def add(cls, jti: str, expires_in: int) -> None:
        """Add a token to the blacklist."""
        client = await get_redis()
        await client.setex(f"{cls.PREFIX}{jti}", expires_in, "1")

    @classmethod
    async def is_blacklisted(cls, jti: str) -> bool:
        """Check if a token is blacklisted."""
        client = await get_redis()
        result = await client.get(f"{cls.PREFIX}{jti}")
        return result is not None


class CacheManager:
    """Simple cache manager using Redis."""

    PREFIX = "cache:"
    DEFAULT_TTL = 300  # 5 minutes

    @classmethod
    async def get(cls, key: str) -> Optional[str]:
        """Get a value from cache."""
        client = await get_redis()
        return await client.get(f"{cls.PREFIX}{key}")

    @classmethod
    async def set(cls, key: str, value: str, ttl: int = DEFAULT_TTL) -> None:
        """Set a value in cache with TTL."""
        client = await get_redis()
        await client.setex(f"{cls.PREFIX}{key}", ttl, value)

    @classmethod
    async def delete(cls, key: str) -> None:
        """Delete a value from cache."""
        client = await get_redis()
        await client.delete(f"{cls.PREFIX}{key}")

    @classmethod
    async def delete_pattern(cls, pattern: str) -> None:
        """Delete all keys matching a pattern."""
        client = await get_redis()
        keys = await client.keys(f"{cls.PREFIX}{pattern}")
        if keys:
            await client.delete(*keys)
