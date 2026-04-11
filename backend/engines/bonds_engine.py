"""
Bonds / Macro Engine — stub (Layer 1).

Layer 2 will implement:
  - FRED API: yield curve (2Y/5Y/10Y/30Y), CPI, PCE, credit spreads
  - yfinance: DXY (^DX-Y.NYB)
  - Central bank rate calendar
"""

from __future__ import annotations


class BondsEngine:
    """Data engine for the Bonds / Macro market page."""

    def __init__(self) -> None:
        pass

    async def get_yield_curve(self) -> dict:
        raise NotImplementedError("BondsEngine.get_yield_curve — Layer 2.")

    async def get_credit_spreads(self) -> dict:
        raise NotImplementedError("BondsEngine.get_credit_spreads — Layer 2.")

    async def get_dxy(self) -> dict:
        raise NotImplementedError("BondsEngine.get_dxy — Layer 2.")

    async def get_inflation(self) -> dict:
        raise NotImplementedError("BondsEngine.get_inflation — Layer 2.")

    async def get_central_bank_rates(self) -> dict:
        raise NotImplementedError("BondsEngine.get_central_bank_rates — Layer 2.")
