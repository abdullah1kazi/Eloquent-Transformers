"""Redis-based caching implementation."""

import json
from typing import Any, Optional

from redis.asyncio import Redis


class RedisCache:
    """
    Redis cache wrapper with async support.

    Demonstrates:
    - Cache-aside pattern
    - Async Redis operations
    - JSON serialization
    """

    def __init__(self, redis_client: Redis, ttl: int = 3600) -> None:
        self._client = redis_client
        self._ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self._client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        serialized = json.dumps(value)
        await self._client.set(key, serialized, ex=ttl or self._ttl)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self._client.exists(key))

    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern."""
        keys = await self._client.keys(pattern)
        if keys:
            await self._client.delete(*keys)
