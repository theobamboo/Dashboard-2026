"""
Shared Pydantic models used across routers and engines.
These are stubs — filled out properly in Layer 2+.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: datetime


class MarketStub(BaseModel):
    """Temporary placeholder returned by stub routers."""
    market: str
    status: str = "not_implemented"
    message: str = "This endpoint will be implemented in Layer 2."


class SignalBase(BaseModel):
    """Base shape for a trading signal / alert."""
    market: str                          # "crypto" | "stocks" | "bonds" | "fx"
    symbol: str
    signal_type: str                     # "buy" | "sell" | "neutral"
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    triggered_at: Optional[datetime] = None
    notes: Optional[str] = None
