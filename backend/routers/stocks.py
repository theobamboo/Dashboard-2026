from fastapi import APIRouter, HTTPException
from backend.engines.stocks_engine import stances
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class AssetStatus(BaseModel):
    price: float
    change_pct: float

class StocksOverviewResponse(BaseModel):
    assets: Dict[str, AssetStatus]
    cached: bool

@router.get("/overview", response_model=StocksOverviewResponse)
async def get_stocks_overview():
    try:
        data = await stances.get_overview()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
