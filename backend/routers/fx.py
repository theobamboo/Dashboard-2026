"""
FX router — stub (Layer 1).
Full implementation in Layer 2: exchangerate.host, CFTC COT data.
"""

from fastapi import APIRouter

from backend.models import MarketStub

router = APIRouter()


@router.get("/", response_model=MarketStub)
async def fx_root() -> MarketStub:
    """FX market overview — not yet implemented."""
    return MarketStub(market="fx")


@router.get("/rates", response_model=MarketStub)
async def fx_rates() -> MarketStub:
    """Major FX pair rates via exchangerate.host."""
    return MarketStub(market="fx", message="FX rates — Layer 2.")


@router.get("/cot", response_model=MarketStub)
async def fx_cot() -> MarketStub:
    """CFTC Commitment of Traders (COT) positioning data."""
    return MarketStub(market="fx", message="COT data — Layer 2.")


@router.get("/correlations", response_model=MarketStub)
async def fx_correlations() -> MarketStub:
    """Cross-pair correlation matrix."""
    return MarketStub(market="fx", message="Correlations — Layer 2.")


@router.get("/carry", response_model=MarketStub)
async def fx_carry() -> MarketStub:
    """Carry trade ranking by interest rate differential."""
    return MarketStub(market="fx", message="Carry trade — Layer 2.")
