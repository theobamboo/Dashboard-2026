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
        """Ensure all percentage fields are populated.
        CoinGecko returns price_change_percentage_XXh for each requested timeframe.
        Alias to _in_currency for clarity. Add bounds checking to catch bad data."""
        if isinstance(data, dict):
            # Map both plain and _in_currency variants to the aliased field names
            for tf_key, plain_key in (
                ("price_change_percentage_1h_in_currency",  "price_change_percentage_1h"),
                ("price_change_percentage_24h_in_currency", "price_change_percentage_24h"),
                ("price_change_percentage_7d_in_currency",  "price_change_percentage_7d"),
            ):
                # Use _in_currency if present and valid, otherwise fall back to plain
                val = data.get(tf_key)
                if val is None:
                    val = data.get(plain_key)
                
                if val is not None:
                    # Clamp unreasonable values (e.g., -168% doesn't make sense)
                    # Allow [-200, 500] range to catch data errors while preserving extreme moves
                    if isinstance(val, (int, float)):
                        clamped = max(-200, min(500, val))
                        if abs(clamped - val) > 0.01:  # Log if clamping happened
                            import logging
                            logging.warning(f"Clamped {plain_key} from {val} to {clamped}")
                        data[tf_key] = clamped
                    else:
                        val = None
                
                # Ensure both the plain and _in_currency keys exist with same value
                if data.get(tf_key) is not None:
                    data[plain_key] = data[tf_key]
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
