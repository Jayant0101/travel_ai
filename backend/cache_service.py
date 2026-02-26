"""
Cache Service (Redis)
======================
Provides caching for:
  1. AI-generated itineraries (expensive Gemini API calls)
  2. Rate limiting counters
  3. Health check status

Falls back gracefully if Redis is unavailable — the app works without it,
just without caching benefits.

Usage:
    cache = CacheService()
    await cache.connect()

    # Cache an itinerary
    await cache.set("itinerary:goa:5days:50000", itinerary_json, ttl=3600)
    cached = await cache.get("itinerary:goa:5days:50000")
"""

import os
import json
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import redis, gracefully degrade if not installed
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed. Caching disabled. Install with: pip install redis")


class CacheService:
    """Async Redis cache service with graceful degradation."""

    def __init__(self):
        self._client = None
        self._connected = False
        self.default_ttl = int(os.environ.get("CACHE_TTL_SECONDS", 3600))

    async def connect(self):
        """Connect to Redis. Silently degrades if unavailable."""
        if not REDIS_AVAILABLE:
            logger.info("Redis library not installed. Running without cache.")
            return

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            self._client = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=3,
                retry_on_timeout=True,
            )
            # Test the connection
            await self._client.ping()
            self._connected = True
            logger.info(f"Redis connected: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self._connected = False

    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client and self._connected:
            await self._client.close()
            self._connected = False
            logger.info("Redis disconnected.")

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache. Returns None on miss or error."""
        if not self._connected:
            return None
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.warning(f"Cache GET failed for '{key}': {e}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set a value in cache with optional TTL."""
        if not self._connected:
            return
        try:
            await self._client.set(key, value, ex=ttl or self.default_ttl)
        except Exception as e:
            logger.warning(f"Cache SET failed for '{key}': {e}")

    async def delete(self, key: str):
        """Delete a key from cache."""
        if not self._connected:
            return
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning(f"Cache DELETE failed for '{key}': {e}")

    async def increment(self, key: str, ttl: int = 60) -> int:
        """
        Increment a counter (for rate limiting).
        Returns the new count. Sets TTL on first increment.
        """
        if not self._connected:
            return 0
        try:
            pipe = self._client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.warning(f"Cache INCREMENT failed for '{key}': {e}")
            return 0

    async def health(self) -> dict:
        """Return cache health status."""
        if not self._connected:
            return {"status": "disconnected", "backend": "none"}
        try:
            await self._client.ping()
            info = await self._client.info("memory")
            return {
                "status": "healthy",
                "backend": "redis",
                "used_memory": info.get("used_memory_human", "unknown"),
            }
        except Exception:
            return {"status": "unhealthy", "backend": "redis"}

    @staticmethod
    def make_itinerary_key(destination: str, days: int, budget: float, preferences: dict) -> str:
        """
        Generate a deterministic cache key for an itinerary request.
        Similar searches will hit the same cache entry.
        """
        # Normalize inputs for better cache hit rate
        normalized = {
            "dest": destination.lower().strip(),
            "days": days,
            "budget_range": round(budget / 10000) * 10000,  # Round to nearest 10K
            "prefs": sorted(k for k, v in preferences.items() if v),
        }
        raw = json.dumps(normalized, sort_keys=True)
        key_hash = hashlib.md5(raw.encode()).hexdigest()[:12]
        return f"itinerary:{key_hash}"


# Singleton instance
cache_service = CacheService()
