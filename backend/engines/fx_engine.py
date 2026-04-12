import httpx
import yfinance as yf
import asyncio
import logging
from typing import Dict, Any
from backend.config import settings
from backend.cache import TTLCache

logger = logging.getLogger(__name__)

class FXEngine:
    """
    Engine for fetching FX data via exchangerate.host and yfinance.
    """
    def __init__(self):
        self.cache = TTLCache(default_ttl=60)
        self.pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "GBP/EUR", "USD/CHF", "AUD/USD"]
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def get_overview(self) -> Dict[str, Any]:
        """
        Fetch major FX pairs and DXY correlation/rates.
        """
        cached = await self.cache.get("fx_overview")
        if cached:
            cached["cached"] = True
            return cached

        fx_rates = await self._fetch_live_rates()

        try:
            dxy_data = await asyncio.to_thread(self._fetch_dxy)
        except Exception as e:
            logger.error(f"Failed to fetch DXY in FX engine: {e}")
            dxy_data = {}

        result = {
            "rates": fx_rates,
            "dxy": dxy_data,
            "cached": False
        }
        await self.cache.set("fx_overview", result)
        return result

    async def _fetch_live_rates(self) -> Dict[str, Any]:
        if not settings.EXCHANGERATE_API_KEY:
            logger.warning("EXCHANGERATE_API_KEY not set")
            # Fall back straight to yfinance
            return await asyncio.to_thread(self._fetch_yf_fx_changes)
            
        try:
            response = await self.client.get(
                f"{settings.EXCHANGERATE_BASE_URL}/live",
                params={
                    "access_key": settings.EXCHANGERATE_API_KEY,
                    "currencies": "EUR,GBP,JPY,CHF,AUD",
                    "source": "USD"
                }
            )
            response.raise_for_status()
            data = response.json()
            quotes = data.get("quotes", {})
            
            usd_eur = quotes.get("USDEUR", 0)
            usd_gbp = quotes.get("USDGBP", 0)
            usd_jpy = quotes.get("USDJPY", 0)
            usd_chf = quotes.get("USDCHF", 0)
            usd_aud = quotes.get("USDAUD", 0)

            rates = {}
            def safe_inv(val): return 1 / val if val else 0
            def safe_div(num, den): return num / den if den else 0

            rates["EUR/USD"] = {"price": safe_inv(usd_eur), "change_pct": 0.0}
            rates["GBP/USD"] = {"price": safe_inv(usd_gbp), "change_pct": 0.0}
            rates["USD/JPY"] = {"price": usd_jpy, "change_pct": 0.0}
            rates["GBP/EUR"] = {"price": safe_div(usd_eur, usd_gbp), "change_pct": 0.0}
            rates["USD/CHF"] = {"price": usd_chf, "change_pct": 0.0}
            rates["AUD/USD"] = {"price": safe_inv(usd_aud), "change_pct": 0.0}
            
            # Exchangerate free tier lacks historical 24h change, patch from yfinance
            yf_updates = await asyncio.to_thread(self._fetch_yf_fx_changes)
            for pair in rates:
                if pair in yf_updates:
                    rates[pair]["change_pct"] = yf_updates[pair]["change_pct"]
                    if rates[pair]["price"] == 0:
                        rates[pair]["price"] = yf_updates[pair]["price"]

            return rates
                
        except Exception as e:
            logger.error(f"exchangerate.host error: {e}")
            fallback_rates = await asyncio.to_thread(self._fetch_yf_fx_changes)
            return fallback_rates

    def _fetch_yf_fx_changes(self) -> Dict[str, Any]:
        pair_to_yf = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "JPY=X",
            "GBP/EUR": "GBPEUR=X",
            "USD/CHF": "CHF=X",
            "AUD/USD": "AUDUSD=X"
        }
        res = {}
        try:
            tickers = yf.Tickers(" ".join(pair_to_yf.values()))
            for pair, yf_sym in pair_to_yf.items():
                ticker = tickers.tickers.get(yf_sym)
                if ticker:
                    fast_info = getattr(ticker, 'fast_info', {})
                    info = getattr(ticker, 'info', {})
                    
                    price = fast_info.get("last_price", info.get("regularMarketPrice", 0))
                    prev_close = fast_info.get("previous_close", info.get("previousClose", 0))
                    change_pct = ((price - prev_close) / prev_close * 100) if prev_close and prev_close > 0 else 0
                    
                    res[pair] = {
                        "price": price,
                        "change_pct": change_pct
                    }
        except Exception as e:
            logger.error(f"yfinance fx fallback error: {e}")
        return res

    def _fetch_dxy(self) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker("DX-Y.NYB")
            fast_info = getattr(ticker, 'fast_info', {})
            info = getattr(ticker, 'info', {})
            
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
stances = FXEngine()
