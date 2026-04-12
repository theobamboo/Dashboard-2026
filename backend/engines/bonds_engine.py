import httpx
import yfinance as yf
import asyncio
import logging
from typing import Dict, Any
from backend.config import settings
from backend.cache import TTLCache

logger = logging.getLogger(__name__)

class BondsEngine:
    """
    Engine for fetching Bonds and Macro data via FRED and yfinance.
    """
    def __init__(self):
        # 5-minute TTL for macro data (FRED updates infrequently)
        self.cache = TTLCache(default_ttl=300)
        self.fred_series = ['DGS2', 'DGS10', 'DGS30', 'FEDFUNDS', 'CPIAUCSL', 'UNRATE']
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def get_overview(self) -> Dict[str, Any]:
        """
        Fetch DGS2, DGS10, DGS30, FEDFUNDS, CPI, Unemployment, and DXY.
        """
        cached = await self.cache.get("bonds_overview")
        if cached:
            cached["cached"] = True
            return cached

        # 1. Fetch FRED data
        fred_data = await self._fetch_fred_data()
        
        # Calculate 2s10s Spread if both exist
        if 'DGS10' in fred_data and 'DGS2' in fred_data:
            fred_data['2s10s_spread'] = {
                "value": fred_data['DGS10']['value'] - fred_data['DGS2']['value'],
                "change": fred_data['DGS10']['change'] - fred_data['DGS2']['change']
            }

        # 2. Fetch DXY via yfinance
        try:
            dxy_data = await asyncio.to_thread(self._fetch_dxy)
        except Exception as e:
            logger.error(f"Failed to fetch DXY: {e}")
            dxy_data = {}

        result = {
            "macro": fred_data,
            "dxy": dxy_data,
            "cached": False
        }
        await self.cache.set("bonds_overview", result)
        return result

    async def _fetch_fred_data(self) -> Dict[str, Any]:
        if not settings.FRED_API_KEY:
            logger.warning("FRED_API_KEY not set in .env")
            return {}

        results = {}
        # Fetch sequentially to respect rate limits or parallelise (FRED is generous)
        for series_id in self.fred_series:
            try:
                response = await self.client.get(
                    settings.FRED_BASE_URL,
                    params={
                        "series_id": series_id,
                        "api_key": settings.FRED_API_KEY,
                        "file_type": "json",
                        "sort_order": "desc",
                        "limit": 2
                    }
                )
                response.raise_for_status()
                data = response.json()
                observations = data.get("observations", [])
                
                valid_obs = [obs for obs in observations if obs.get("value") != "."]
                
                if not valid_obs:
                    continue

                current_val = float(valid_obs[0]["value"])
                prev_val = float(valid_obs[1]["value"]) if len(valid_obs) > 1 else current_val
                
                change = current_val - prev_val
                
                results[series_id] = {
                    "value": current_val,
                    "change": change
                }
            except Exception as e:
                logger.error(f"FRED fetch error for {series_id}: {e}")

        return results

    def _fetch_dxy(self) -> Dict[str, Any]:
        """
        Synchronous fetch for DXY using yfinance.
        """
        try:
            ticker = yf.Ticker("DX-Y.NYB")
            fast_info = ticker.fast_info
            info = ticker.info
            
            price = fast_info.get("last_price", info.get("regularMarketPrice", 0))
            prev_close = fast_info.get("previous_close", info.get("previousClose", 0))
            
            change_pct = ((price - prev_close) / prev_close * 100) if prev_close and prev_close > 0 else 0
            
            return {
                "price": price,
                "change_pct": change_pct
            }
        except Exception as e:
            logger.error(f"yfinance DXY error: {e}")
            return {}

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

# Singleton
stances = BondsEngine()
