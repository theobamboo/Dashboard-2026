"""
FX Engine — stub (Layer 1).

Layer 2 will implement:
  - exchangerate.host: live FX pair rates
  - CFTC COT data: weekly positioning for major pairs
  - Carry trade ranking by interest rate differential
  - Cross-pair correlation matrix
"""

from __future__ import annotations


class FXEngine:
    """Data engine for the FX market page."""

    def __init__(self) -> None:
        pass

    async def get_rates(self, base: str = "USD") -> dict:
        raise NotImplementedError("FXEngine.get_rates — Layer 2.")

    async def get_cot_data(self) -> dict:
        raise NotImplementedError("FXEngine.get_cot_data — Layer 2.")

    async def get_correlations(self, pairs: list[str]) -> dict:
        raise NotImplementedError("FXEngine.get_correlations — Layer 2.")

    async def get_carry_ranking(self) -> list[dict]:
        raise NotImplementedError("FXEngine.get_carry_ranking — Layer 2.")
