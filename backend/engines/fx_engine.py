import httpx
import yfinance as yf
import asyncio
import logging
from typing import Dict, Any, Optional
from backend.config import settings
from backend.cache import TTLCache

logger = logging.getLogger(__name__)

# Safe empty rates structure used as a fallback so the API never returns null
_EMPTY_RATES: Dict[str, Any] = {
    pair: {"price": 0.0, "change_pct": 0.0}
    for pair in ["EUR/USD", "GBP/USD", "USD/JPY", "GBP/EUR", "USD/CHF", "AUD/USD"]
}


class FXEngine:
    """
    Engine for fetching FX data via exchangerate.host and yfinance.
    All public methods are guaranteed to return a valid dict — never raise.
    """

    def __init__(self):
        self.cache = TTLCache(default_ttl=60)
        self.pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "GBP/EUR", "USD/CHF", "AUD/USD"]
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def get_overview(self) -> Dict[str, Any]:
        """
        Fetch major FX pairs and DXY. Never raises — returns empty-safe result on failure.
        """
        try:
            cached = self.cache.get("fx_overview")
            if cached:
                cached["cached"] = True
                return cached
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        try:
            fx_rates = await self._fetch_live_rates()
        except Exception as e:
            logger.error(f"FX rates fetch failed: {e}")
            fx_rates = dict(_EMPTY_RATES)

        # Guarantee every expected pair is present in the response
        for pair in self.pairs:
            if pair not in fx_rates:
                fx_rates[pair] = {"price": 0.0, "change_pct": 0.0}

        try:
            dxy_data = await asyncio.to_thread(self._fetch_dxy)
        except Exception as e:
            logger.error(f"DXY fetch failed: {e}")
            dxy_data = {"price": 0.0, "change_pct": 0.0}

        result = {
            "rates": fx_rates,
            "dxy": dxy_data,
            "cached": False,
        }

        try:
            self.cache.set("fx_overview", result)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

        return result

    async def _fetch_live_rates(self) -> Dict[str, Any]:
        if not settings.EXCHANGERATE_API_KEY:
            logger.warning("EXCHANGERATE_API_KEY not set — falling back to yfinance")
            return await asyncio.to_thread(self._fetch_yf_fx_changes)

        try:
            response = await self.client.get(
                f"{settings.EXCHANGERATE_BASE_URL}/live",
                params={
                    "access_key": settings.EXCHANGERATE_API_KEY,
                    "currencies": "EUR,GBP,JPY,CHF,AUD",
                    "source": "USD",
                },
            )
            response.raise_for_status()
            data = response.json()
            quotes = data.get("quotes", {})

            usd_eur = quotes.get("USDEUR", 0)
            usd_gbp = quotes.get("USDGBP", 0)
            usd_jpy = quotes.get("USDJPY", 0)
            usd_chf = quotes.get("USDCHF", 0)
            usd_aud = quotes.get("USDAUD", 0)

            def safe_inv(val: float) -> float:
                return 1.0 / val if val else 0.0

            def safe_div(num: float, den: float) -> float:
                return num / den if den else 0.0

            rates = {
                "EUR/USD": {"price": safe_inv(usd_eur), "change_pct": 0.0},
                "GBP/USD": {"price": safe_inv(usd_gbp), "change_pct": 0.0},
                "USD/JPY": {"price": float(usd_jpy),    "change_pct": 0.0},
                "GBP/EUR": {"price": safe_div(usd_eur, usd_gbp), "change_pct": 0.0},
                "USD/CHF": {"price": float(usd_chf),    "change_pct": 0.0},
                "AUD/USD": {"price": safe_inv(usd_aud), "change_pct": 0.0},
            }

            # Patch 24h change_pct from yfinance (exchangerate free tier has no history)
            try:
                yf_updates = await asyncio.to_thread(self._fetch_yf_fx_changes)
                for pair in rates:
                    if pair in yf_updates:
                        rates[pair]["change_pct"] = yf_updates[pair].get("change_pct", 0.0)
                        if rates[pair]["price"] == 0.0:
                            rates[pair]["price"] = yf_updates[pair].get("price", 0.0)
            except Exception as e:
                logger.warning(f"yfinance change_pct patch failed: {e}")

            return rates

        except Exception as e:
            logger.error(f"exchangerate.host error: {e} — falling back to yfinance")
            try:
                return await asyncio.to_thread(self._fetch_yf_fx_changes)
            except Exception as e2:
                logger.error(f"yfinance fallback also failed: {e2}")
                return dict(_EMPTY_RATES)

    def _fetch_yf_fx_changes(self) -> Dict[str, Any]:
        pair_to_yf = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "JPY=X",
            "GBP/EUR": "GBPEUR=X",
            "USD/CHF": "CHF=X",
            "AUD/USD": "AUDUSD=X",
        }
        res: Dict[str, Any] = {}
        try:
            tickers = yf.Tickers(" ".join(pair_to_yf.values()))
            for pair, yf_sym in pair_to_yf.items():
                try:
                    ticker = tickers.tickers.get(yf_sym)
                    if not ticker:
                        res[pair] = {"price": 0.0, "change_pct": 0.0}
                        continue

                    fast_info = getattr(ticker, "fast_info", None)

                    # ticker.info makes an HTTP call in yfinance v0.2+ and can
                    # raise HTTPError on rate-limits or invalid symbols — guard it.
                    try:
                        info: dict = ticker.info or {}
                    except Exception:
                        info = {}

                    # fast_info may itself be None — use getattr with a None default
                    fi_price = getattr(fast_info, "last_price", None)
                    fi_prev  = getattr(fast_info, "previous_close", None)

                    price = float(
                        fi_price
                        if fi_price is not None
                        else (info.get("regularMarketPrice") or 0.0)
                    )
                    prev_close = float(
                        fi_prev
                        if fi_prev is not None
                        else (info.get("previousClose") or 0.0)
                    )
                    change_pct = (
                        (price - prev_close) / prev_close * 100.0
                        if prev_close > 0
                        else 0.0
                    )
                    res[pair] = {"price": price, "change_pct": change_pct}
                except Exception as e:
                    logger.warning(f"yfinance error for {pair}: {e}")
                    res[pair] = {"price": 0.0, "change_pct": 0.0}
        except Exception as e:
            logger.error(f"yfinance Tickers bulk fetch error: {e}")
        return res

    def _fetch_dxy(self) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker("DX-Y.NYB")
            fast_info = getattr(ticker, "fast_info", None)

            # ticker.info raises in yfinance v0.2+ on rate-limits — guard it.
            try:
                info: dict = ticker.info or {}
            except Exception:
                info = {}

            fi_price = getattr(fast_info, "last_price", None)
            fi_prev  = getattr(fast_info, "previous_close", None)

            price = float(
                fi_price
                if fi_price is not None
                else (info.get("regularMarketPrice") or 0.0)
            )
            prev_close = float(
                fi_prev
                if fi_prev is not None
                else (info.get("previousClose") or 0.0)
            )
            change_pct = (
                (price - prev_close) / prev_close * 100.0
                if prev_close > 0
                else 0.0
            )
            return {"price": price, "change_pct": change_pct}
        except Exception as e:
            logger.error(f"DXY fetch error: {e}")
            return {"price": 0.0, "change_pct": 0.0}

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Module-level singleton (imported by routers/fx.py as `stances`)
stances = FXEngine()
