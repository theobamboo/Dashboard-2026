"""
Stocks Engine — stub (Layer 1).

Layer 2 will implement:
  - yfinance: quote, OHLCV history, sector data
  - CBOE: VIX spot + term structure, equity put/call ratio
  - Momentum + volume breakout screener
"""

from __future__ import annotations


class StocksEngine:
    """Data engine for the Stocks / ETFs market page."""

    def __init__(self) -> None:
        pass

    async def get_quote(self, ticker: str) -> dict:
        raise NotImplementedError("StocksEngine.get_quote — Layer 2.")

    async def get_vix(self) -> dict:
        raise NotImplementedError("StocksEngine.get_vix — Layer 2.")

    async def get_put_call_ratio(self) -> dict:
        raise NotImplementedError("StocksEngine.get_put_call_ratio — Layer 2.")

    async def run_screener(self, universe: list[str]) -> list[dict]:
        raise NotImplementedError("StocksEngine.run_screener — Layer 2.")

    async def get_etf_flows(self) -> dict:
        raise NotImplementedError("StocksEngine.get_etf_flows — Layer 2.")
