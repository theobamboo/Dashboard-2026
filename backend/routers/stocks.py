"""
Stocks / ETFs router — stub (Layer 1).
Full implementation in Layer 2: yfinance, CBOE (VIX, Put/Call ratio).
"""

from fastapi import APIRouter

from backend.models import MarketStub

router = APIRouter()


@router.get("/", response_model=MarketStub)
async def stocks_root() -> MarketStub:
    """Stocks & ETFs market overview — not yet implemented."""
    return MarketStub(market="stocks")


@router.get("/quote", response_model=MarketStub)
async def stocks_quote() -> MarketStub:
    """Single ticker quote via yfinance."""
    return MarketStub(market="stocks", message="yfinance quote — Layer 2.")


@router.get("/screener", response_model=MarketStub)
async def stocks_screener() -> MarketStub:
    """Swing trade screener (momentum, volume breakout)."""
    return MarketStub(market="stocks", message="Screener — Layer 2.")


@router.get("/vix", response_model=MarketStub)
async def stocks_vix() -> MarketStub:
    """VIX spot + term structure from CBOE / yfinance."""
    return MarketStub(market="stocks", message="VIX — Layer 2.")


@router.get("/put-call-ratio", response_model=MarketStub)
async def stocks_put_call_ratio() -> MarketStub:
    """Equity put/call ratio from CBOE."""
    return MarketStub(market="stocks", message="Put/Call ratio — Layer 2.")


@router.get("/etf-flows", response_model=MarketStub)
async def stocks_etf_flows() -> MarketStub:
    """Sector ETF flow data."""
    return MarketStub(market="stocks", message="ETF flows — Layer 2.")
