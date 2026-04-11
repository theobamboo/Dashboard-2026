"""
Crypto Engine — stub (Layer 1).

Layer 2 will implement:
  - CoinGecko: price feeds, market cap, volume, dominance
  - CoinGlass: funding rates, liquidation heatmap, open interest
  - CryptoQuant: on-chain flows, miner revenue, exchange reserve
  - IntoTheBlock: large-tx counts, in/out of money, holder distribution
  - Alternative.me: Fear & Greed index
"""

from __future__ import annotations


class CryptoEngine:
    """Data engine for the Crypto market page."""

    def __init__(self) -> None:
        # HTTP client and caches will be initialised in Layer 2
        pass

    async def get_prices(self, top_n: int = 100) -> dict:
        raise NotImplementedError("CryptoEngine.get_prices — Layer 2.")

    async def get_funding_rates(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_funding_rates — Layer 2.")

    async def get_liquidations(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_liquidations — Layer 2.")

    async def get_open_interest(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_open_interest — Layer 2.")

    async def get_fear_greed(self) -> dict:
        raise NotImplementedError("CryptoEngine.get_fear_greed — Layer 2.")

    async def get_onchain(self, symbol: str) -> dict:
        raise NotImplementedError("CryptoEngine.get_onchain — Layer 2.")
