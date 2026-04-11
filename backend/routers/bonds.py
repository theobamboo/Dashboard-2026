"""
Bonds / Macro router — stub (Layer 1).
Full implementation in Layer 2: FRED API, DXY via yfinance.
"""

from fastapi import APIRouter

from backend.models import MarketStub

router = APIRouter()


@router.get("/", response_model=MarketStub)
async def bonds_root() -> MarketStub:
    """Bonds & macro overview — not yet implemented."""
    return MarketStub(market="bonds")


@router.get("/yield-curve", response_model=MarketStub)
async def bonds_yield_curve() -> MarketStub:
    """US Treasury yield curve (2Y, 5Y, 10Y, 30Y) via FRED."""
    return MarketStub(market="bonds", message="Yield curve — Layer 2.")


@router.get("/spreads", response_model=MarketStub)
async def bonds_spreads() -> MarketStub:
    """Credit spreads (IG, HY) via FRED."""
    return MarketStub(market="bonds", message="Credit spreads — Layer 2.")


@router.get("/central-banks", response_model=MarketStub)
async def bonds_central_banks() -> MarketStub:
    """Central bank rate decisions and forward guidance."""
    return MarketStub(market="bonds", message="Central banks — Layer 2.")


@router.get("/dxy", response_model=MarketStub)
async def bonds_dxy() -> MarketStub:
    """DXY Dollar Index via yfinance."""
    return MarketStub(market="bonds", message="DXY — Layer 2.")


@router.get("/cpi-pce", response_model=MarketStub)
async def bonds_inflation() -> MarketStub:
    """CPI & PCE inflation data via FRED."""
    return MarketStub(market="bonds", message="CPI/PCE — Layer 2.")
