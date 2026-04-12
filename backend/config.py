"""
Centralised configuration loaded from .env via python-dotenv.
All secrets and tuneable constants live here — import `settings` everywhere.
"""

from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()  # reads .env from project root (one level up from backend/)


class Settings:
    # -----------------------------------------------------------------------
    # App meta
    # -----------------------------------------------------------------------
    APP_VERSION: str = "0.1.0"
    ENV: str = os.getenv("ENV", "development")

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite React dev server
        "http://localhost:3000",   # CRA fallback
        "http://127.0.0.1:5173",
    ]

    # -----------------------------------------------------------------------
    # Crypto data sources
    # -----------------------------------------------------------------------
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_PRO_KEY: str = os.getenv("COINGECKO_PRO_KEY", "")

    COINGLASS_BASE_URL: str = "https://open-api.coinglass.com/public/v2"
    COINGLASS_KEY: str = os.getenv("COINGLASS_KEY", "")

    CRYPTOQUANT_KEY: str = os.getenv("CRYPTOQUANT_KEY", "")
    INTOTHEBLOCK_KEY: str = os.getenv("INTOTHEBLOCK_KEY", "")

    FEAR_GREED_URL: str = "https://api.alternative.me/fng/"

    # -----------------------------------------------------------------------
    # Macro / Stocks / FX
    # -----------------------------------------------------------------------
    FRED_API_KEY: str = os.getenv("FRED_API_KEY", "")
    FRED_BASE_URL: str = "https://api.stlouisfed.org/fred/series/observations"

    EXCHANGERATE_BASE_URL: str = "https://api.exchangerate.host"
    EXCHANGERATE_API_KEY: str = os.getenv("EXCHANGERATE_API_KEY", "")
    # -----------------------------------------------------------------------
    # Telegram alerts
    # -----------------------------------------------------------------------
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database/trading.db")


settings = Settings()
