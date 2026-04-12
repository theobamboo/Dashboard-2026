from fastapi import APIRouter, HTTPException
from backend.engines.fx_engine import stances
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter()

class FxRate(BaseModel):
    price: float
    change_pct: float

class DxyStatus(BaseModel):
    price: float
    change_pct: float

class FxOverviewResponse(BaseModel):
    rates: Dict[str, FxRate]
    dxy: Optional[DxyStatus] = None
    cached: bool

@router.get("/overview", response_model=FxOverviewResponse)
async def get_fx_overview():
    try:
        data = await stances.get_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
