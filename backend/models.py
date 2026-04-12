"""
Pydantic response models — shared across routers and engines.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime


class MarketStub(BaseModel):
    """Temporary placeholder returned by unimplemented stub routers."""
    market: str
    status: str = "not_implemented"
    message: str = "This endpoint will be implemented in a future layer."


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class SignalBase(BaseModel):
    """Base shape for a trading signal / alert."""
    market: str                          # "crypto" | "stocks" | "bonds" | "fx"
    symbol: str
    signal_type: str                     # "buy" | "sell" | "neutral"
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    triggered_at: Optional[datetime] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Crypto — CoinGecko /coins/markets
# ---------------------------------------------------------------------------

class CoinPrice(BaseModel):
    id: str
    symbol: str
    name: str
    image: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    total_volume: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    # These are populated when price_change_percentage=1h,24h,7d is requested.
    # The _in_currency aliases are the accurate per-currency values; the plain
    # fields (e.g. price_change_percentage_24h) are always returned by CoinGecko
    # and serve as the fallback.
    price_change_percentage_1h: Optional[float] = Field(None, alias="price_change_percentage_1h_in_currency")
    price_change_percentage_24h: Optional[float] = Field(None, alias="price_change_percentage_24h_in_currency")
    price_change_percentage_7d: Optional[float] = Field(None, alias="price_change_percentage_7d_in_currency")
    # Raw plain fields (always present from CoinGecko) — used as fallbacks
    _raw_pct_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    ath: Optional[float] = None
    ath_change_percentage: Optional[float] = None
    last_updated: Optional[str] = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _fill_pct_fallbacks(cls, data: dict) -> dict:
        """If the _in_currency variants are absent/null, fall back to the plain
        price_change_percentage_* fields that CoinGecko always returns."""
        if isinstance(data, dict):
            for tf_key, plain_key in (
                ("price_change_percentage_1h_in_currency",  "price_change_percentage_1h"),
                ("price_change_percentage_24h_in_currency", "price_change_percentage_24h"),
                ("price_change_percentage_7d_in_currency",  "price_change_percentage_7d"),
            ):
                if data.get(tf_key) is None and data.get(plain_key) is not None:
                    data[tf_key] = data[plain_key]
        return data


class PricesResponse(BaseModel):
    coins: list[CoinPrice]
    count: int
    cached: bool
    fetched_at: str


# ---------------------------------------------------------------------------
# Crypto — CoinGecko /global (dominance)
# ---------------------------------------------------------------------------

class DominanceResponse(BaseModel):
    btc_dominance: float
    eth_dominance: float
    total_market_cap_usd: float
    total_volume_24h_usd: float
    market_cap_change_24h_pct: float
    active_cryptocurrencies: int
    markets: int
    cached: bool
    fetched_at: str


# ---------------------------------------------------------------------------
# Crypto — Alternative.me Fear & Greed
# ---------------------------------------------------------------------------

class FearGreedEntry(BaseModel):
    value: int
    classification: str
    timestamp: int


class FearGreedResponse(BaseModel):
    current: FearGreedEntry
    history: list[FearGreedEntry]   # last 7 days
    cached: bool
    fetched_at: str
