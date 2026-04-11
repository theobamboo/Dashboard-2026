from typing import Dict, Any, List
import yfinance as yf
import asyncio
from backend.cache import TTLCache
import logging

logger = logging.getLogger(__name__)

class StocksEngine:
    """
    Engine for fetching Stocks, ETFs, and VIX data via yfinance.
    """
    def __init__(self):
        # 1-minute TTL for stock quotes
        self.cache = TTLCache(ttl_seconds=60)
        self.symbols = ['SPY', 'QQQ', '^VIX']

    async def get_overview(self) -> Dict[str, Any]:
        """
        Fetch SPY, QQQ, VIX, and mock Put/Call ratio.
        """
        # Check cache first
        cached = await self.cache.get("stocks_overview")
        if cached:
            cached["cached"] = True
            return cached

        try:
            # Run yfinance blocking calls in a background thread to prevent blocking async event loop
            data = await asyncio.to_thread(self._fetch_yf_data)
        except Exception as e:
            logger.error(f"Failed to fetch yf data: {e}")
            data = {}

        # Mock CBOE PCR for now as it requires Cloudflare bypass
        data["PCR"] = {
            "price": 0.85,
            "change_pct": 1.2
        }

        result = {
            "assets": data,
            "cached": False
        }
        await self.cache.set("stocks_overview", result)
        return result

    def _fetch_yf_data(self) -> Dict[str, Any]:
        """
        Synchronous fetch using yfinance.
        """
        try:
            tickers = yf.Tickers(" ".join(self.symbols))
            res = {}
            for sym in self.symbols:
                ticker = tickers.tickers.get(sym)
                if ticker:
                    fast_info = ticker.fast_info
                    info = ticker.info
                    
                    price = fast_info.get("last_price", info.get("currentPrice", info.get("regularMarketPrice", 0)))
                    prev_close = fast_info.get("previous_close", info.get("previousClose", 0))
                    
                    # Prevent division by zero
                    change_pct = ((price - prev_close) / prev_close * 100) if prev_close and prev_close > 0 else 0
                    
                    res[sym] = {
                        "price": price,
                        "change_pct": change_pct
                    }
            return res
        except Exception as e:
            logger.error(f"yfinance fetch error: {e}")
            return {}

# Singleton
stances = StocksEngine()
