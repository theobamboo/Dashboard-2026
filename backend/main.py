"""
Living the Dream Trading — Backend API
Entry point: uvicorn backend.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.engines.crypto_engine import crypto_engine
from backend.routers import crypto, stocks, bonds, fx


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing to initialise — engines use lazy client creation
    yield
    # Shutdown: close async HTTP clients
    await crypto_engine.close()

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Living the Dream Trading API",
    description=(
        "Swing trading dashboard API. "
        "Covers Crypto, Stocks/ETFs, Bonds/Macro, and FX markets."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow React dev server (Vite default: 5173) and production origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Market routers
# ---------------------------------------------------------------------------
app.include_router(crypto.router, prefix="/api/v1/crypto",  tags=["Crypto"])
app.include_router(stocks.router, prefix="/api/v1/stocks",  tags=["Stocks / ETFs"])
app.include_router(bonds.router,  prefix="/api/v1/bonds",   tags=["Bonds / Macro"])
app.include_router(fx.router,     prefix="/api/v1/fx",      tags=["FX"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health() -> dict:
    """Quick liveness probe — returns version and server timestamp."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/", tags=["System"])
async def root() -> dict:
    return {"message": "Living the Dream Trading API — see /docs for endpoints."}
