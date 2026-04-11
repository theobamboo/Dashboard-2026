"""
Crypto router — Layer 2.
Live endpoints: prices, dominance, fear-greed.
Stubs: funding-rates, liquidations, open-interest, on-chain.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from backend.engines.crypto_engine import crypto_engine
from backend.models import (
    DominanceResponse,
    FearGreedResponse,
    MarketStub,
    PricesResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Live endpoints
# ---------------------------------------------------------------------------

@router.get("/", summary="Crypto market overview")
async def crypto_root() -> dict:
    """
    Quick overview: dominance + Fear & Greed in one call.
    Combines /dominance and /fear-greed with shared cache — very cheap.
    """
    try:
        dominance = await crypto_engine.get_dominance()
        fg = await crypto_engine.get_fear_greed(days=1)
        return {
            "market": "crypto",
            "btc_dominance": dominance.btc_dominance,
            "eth_dominance": dominance.eth_dominance,
            "total_market_cap_usd": dominance.total_market_cap_usd,
            "market_cap_change_24h_pct": dominance.market_cap_change_24h_pct,
            "fear_greed": {
                "value": fg.current.value,
                "classification": fg.current.classification,
            },
            "fetched_at": dominance.fetched_at,
        }
    except Exception as exc:
        logger.exception("crypto_root failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get(
    "/prices",
    response_model=PricesResponse,
    summary="Top-N coin prices (CoinGecko)",
)
async def crypto_prices(
    top: int = Query(default=100, ge=1, le=250, description="Number of coins (max 250)"),
) -> PricesResponse:
    """
    Market data for the top-N coins by market cap.
    Includes 1h / 24h / 7d % change. Cached for 60 s.
    """
    try:
        return await crypto_engine.get_prices(top_n=top)
    except Exception as exc:
        logger.exception("crypto_prices failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get(
    "/dominance",
    response_model=DominanceResponse,
    summary="BTC/ETH market dominance (CoinGecko /global)",
)
async def crypto_dominance() -> DominanceResponse:
    """
    BTC & ETH dominance %, total market cap, 24h volume.
    Cached for 5 min.
    """
    try:
        return await crypto_engine.get_dominance()
    except Exception as exc:
        logger.exception("crypto_dominance failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


@router.get(
    "/fear-greed",
    response_model=FearGreedResponse,
    summary="Fear & Greed index (Alternative.me)",
)
async def crypto_fear_greed(
    days: int = Query(default=7, ge=1, le=30, description="Days of history"),
) -> FearGreedResponse:
    """
    Current Fear & Greed value + N-day history.
    Cached for 5 min (index updates daily).
    """
    try:
        return await crypto_engine.get_fear_greed(days=days)
    except Exception as exc:
        logger.exception("crypto_fear_greed failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))


# ---------------------------------------------------------------------------
# Stubs (Layer 3 — require CoinGlass / CryptoQuant keys)
# ---------------------------------------------------------------------------

@router.get("/funding-rates", response_model=MarketStub, summary="Perp funding rates [stub]")
async def crypto_funding_rates() -> MarketStub:
    return MarketStub(market="crypto", message="Funding rates via CoinGlass — Layer 3.")


@router.get("/liquidations", response_model=MarketStub, summary="Liquidation heatmap data [stub]")
async def crypto_liquidations() -> MarketStub:
    return MarketStub(market="crypto", message="Liquidations via CoinGlass — Layer 3.")


@router.get("/open-interest", response_model=MarketStub, summary="Aggregated open interest [stub]")
async def crypto_open_interest() -> MarketStub:
    return MarketStub(market="crypto", message="Open interest via CoinGlass — Layer 3.")


@router.get("/onchain", response_model=MarketStub, summary="On-chain metrics [stub]")
async def crypto_onchain() -> MarketStub:
    return MarketStub(market="crypto", message="On-chain via CryptoQuant / IntoTheBlock — Layer 3.")
