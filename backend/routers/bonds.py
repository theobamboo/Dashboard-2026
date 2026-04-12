from fastapi import APIRouter, HTTPException
from backend.engines.bonds_engine import stances
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()

class MacroStatus(BaseModel):
    value: float
    change: float

class DxyStatus(BaseModel):
    price: float
    change_pct: float

class BondsOverviewResponse(BaseModel):
    macro: Dict[str, MacroStatus]
    dxy: Optional[DxyStatus] = None
    cached: bool

@router.get("/overview", response_model=BondsOverviewResponse)
async def get_bonds_overview():
    """Bonds & macro overview integrating FRED and yfinance DXY."""
    try:
        data = await stances.get_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
