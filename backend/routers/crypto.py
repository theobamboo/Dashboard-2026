"""
Crypto router — stub (Layer 1).
Full implementation in Layer 2: CoinGecko, CoinGlass, CryptoQuant,
IntoTheBlock, Alternative.me (Fear & Greed).
"""

from fastapi import APIRouter

from backend.models import MarketStub

router = APIRouter()


@router.get("/", response_model=MarketStub)
async def crypto_root() -> MarketStub:
    """Crypto market overview — not yet implemented."""
    return MarketStub(market="crypto")


@router.get("/prices", response_model=MarketStub)
async def crypto_prices() -> MarketStub:
    """Top-N coin prices from CoinGecko."""
    return MarketStub(market="crypto", message="CoinGecko price feed — Layer 2.")


@router.get("/dominance", response_model=MarketStub)
async def crypto_dominance() -> MarketStub:
    """BTC/ETH market dominance."""
    return MarketStub(market="crypto", message="Dominance — Layer 2.")


@router.get("/funding-rates", response_model=MarketStub)
async def crypto_funding_rates() -> MarketStub:
    """Perpetual futures funding rates via CoinGlass."""
    return MarketStub(market="crypto", message="Funding rates — Layer 2.")


@router.get("/liquidations", response_model=MarketStub)
async def crypto_liquidations() -> MarketStub:
    """Liquidation heatmap data via CoinGlass."""
    return MarketStub(market="crypto", message="Liquidations — Layer 2.")


@router.get("/open-interest", response_model=MarketStub)
async def crypto_open_interest() -> MarketStub:
    """Aggregated open interest via CoinGlass."""
    return MarketStub(market="crypto", message="Open interest — Layer 2.")


@router.get("/fear-greed", response_model=MarketStub)
async def crypto_fear_greed() -> MarketStub:
    """Fear & Greed index via Alternative.me."""
    return MarketStub(market="crypto", message="Fear & Greed — Layer 2.")


@router.get("/onchain", response_model=MarketStub)
async def crypto_onchain() -> MarketStub:
    """On-chain metrics via CryptoQuant & IntoTheBlock."""
    return MarketStub(market="crypto", message="On-chain metrics — Layer 2.")
