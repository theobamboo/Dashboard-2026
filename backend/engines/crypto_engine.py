"""
Crypto Engine — Layer 2.

Live data sources:
  - CoinGecko (free tier): /coins/markets, /global
  - Alternative.me: Fear & Greed index (no key required)

Stubs still in place (Layer 3+):
  - CoinGlass: funding rates, liquidations, open interest
  - CryptoQuant + IntoTheBlock: on-chain metrics

Rate limit notes:
  - CoinGecko free: ~10-50 calls/min → cache 60s (prices), 300s (global)
  - Alternative.me: generous, cache 300s (updates once per day)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from backend.cache import TTLCache
from backend.config import settings
from backend.models import (
    CoinPrice,
    DominanceResponse,
    FearGreedEntry,
    FearGreedResponse,
    PricesResponse,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTL constants (seconds)
# ---------------------------------------------------------------------------
TTL_PRICES = 60          # CoinGecko market data — 1 min
TTL_DOMINANCE = 300      # CoinGecko global — 5 min
TTL_FEAR_GREED = 300     # Alternative.me — 5 min (API updates once/day)


class CryptoEngine:
    """
    Async data engine for the Crypto market page.
    Instantiate once and reuse (holds a shared httpx client + TTL cache).
    """

    def __init__(self) -> None:
        self._cache = TTLCache()
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Lifecycle helpers (call in FastAPI lifespan or on first use)
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Return (or lazily create) the shared async HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {"Accept": "application/json"}
            if settings.COINGECKO_PRO_KEY:
                headers["x-cg-pro-api-key"] = settings.COINGECKO_PRO_KEY
            self._client = httpx.AsyncClient(
                base_url=settings.COINGECKO_BASE_URL,
                headers=headers,
                timeout=15.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client — call on app shutdown."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------
    # Internal fetch helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        client = await self._get_client()
        resp = await client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_prices(self, top_n: int = 100) -> PricesResponse:
        """
        Top-N coins by market cap from CoinGecko /coins/markets.
        Returns structured PricesResponse — cached for 60 s.
        """
        cache_key = f"prices:{top_n}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        logger.info("Fetching prices for top-%d coins from CoinGecko", top_n)
        raw: list[dict] = await self._get(
            "/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": min(top_n, 250),
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "1h,24h,7d",
            },
        )

        coins = [CoinPrice.model_validate(item) for item in raw]
        result = PricesResponse(
            coins=coins,
            count=len(coins),
            cached=False,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
        self._cache.set(cache_key, result, ttl=TTL_PRICES)
        return result

    async def get_dominance(self) -> DominanceResponse:
        """
        BTC/ETH dominance + total market cap from CoinGecko /global.
        Cached for 5 min.
        """
        cache_key = "dominance"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        logger.info("Fetching global market data from CoinGecko")
        raw: dict = await self._get("/global")
        data: dict = raw["data"]

        mcp = data.get("market_cap_percentage", {})
        result = DominanceResponse(
            btc_dominance=round(mcp.get("btc", 0.0), 4),
            eth_dominance=round(mcp.get("eth", 0.0), 4),
            total_market_cap_usd=data["total_market_cap"].get("usd", 0.0),
            total_volume_24h_usd=data["total_volume"].get("usd", 0.0),
            market_cap_change_24h_pct=data.get("market_cap_change_percentage_24h_usd", 0.0),
            active_cryptocurrencies=data.get("active_cryptocurrencies", 0),
            markets=data.get("markets", 0),
            cached=False,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
        self._cache.set(cache_key, result, ttl=TTL_DOMINANCE)
        return result

    async def get_fear_greed(self, days: int = 7) -> FearGreedResponse:
        """
        Fear & Greed index (current + last N days) from Alternative.me.
        Cached for 5 min.
        """
        cache_key = f"fear_greed:{days}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        logger.info("Fetching Fear & Greed index from Alternative.me")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                settings.FEAR_GREED_URL,
                params={"limit": days, "format": "json"},
            )
            resp.raise_for_status()
            raw: dict = resp.json()

        entries = [
            FearGreedEntry(
                value=int(item["value"]),
                classification=item["value_classification"],
                timestamp=int(item["timestamp"]),
            )
            for item in raw["data"]
        ]

        result = FearGreedResponse(
            current=entries[0],
            history=entries,
            cached=False,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
        self._cache.set(cache_key, result, ttl=TTL_FEAR_GREED)
        return result

    def cache_stats(self) -> dict:
        """Expose cache diagnostics for the /health endpoint."""
        return self._cache.stats()

    # ------------------------------------------------------------------
    # Layer 3+ stubs — CoinGlass / CryptoQuant / IntoTheBlock
    # ------------------------------------------------------------------

    async def get_funding_rates(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_funding_rates — Layer 3 (CoinGlass key required).")

    async def get_liquidations(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_liquidations — Layer 3 (CoinGlass key required).")

    async def get_open_interest(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_open_interest — Layer 3 (CoinGlass key required).")

    async def get_onchain(self, symbol: str) -> dict:
        raise NotImplementedError("CryptoEngine.get_onchain — Layer 3 (CryptoQuant / IntoTheBlock key required).")


# ---------------------------------------------------------------------------
# Module-level singleton — imported by the router
# ---------------------------------------------------------------------------
crypto_engine = CryptoEngine()
