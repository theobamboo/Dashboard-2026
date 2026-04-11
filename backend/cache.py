"""
Lightweight async-safe TTL cache.
Used by all engines to avoid hammering rate-limited APIs.

Usage:
    from backend.cache import TTLCache

    _cache = TTLCache()

    async def get_prices():
        cached = _cache.get("prices")
        if cached:
            return cached
        data = await fetch_from_api()
        _cache.set("prices", data, ttl=60)
        return data
"""

from __future__ import annotations

import time
from typing import Any, Optional


class TTLCache:
    """
    Simple in-memory key/value cache with per-entry TTL (seconds).
    Thread-safe for single-process asyncio — no locking needed.
    """

    def __init__(self, default_ttl: int = 60) -> None:
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if not expired, else None."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value with TTL (seconds). Defaults to instance default_ttl."""
        ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = (value, time.monotonic() + ttl)

    def invalidate(self, key: str) -> None:
        """Manually evict a key."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Wipe all entries."""
        self._store.clear()

    def stats(self) -> dict:
        """Diagnostic info — useful for the /health endpoint."""
        now = time.monotonic()
        live = sum(1 for _, (_, exp) in self._store.items() if exp > now)
        return {"total_keys": len(self._store), "live_keys": live}
