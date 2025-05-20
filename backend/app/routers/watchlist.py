from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter() 

# Optional: in-memory store (for now)
watchlist = set()

class TickerRequest(BaseModel):
    ticker: str

@router.post("/add")
def add_ticker(req: TickerRequest):
    watchlist.add(req.ticker.upper())
    return {"message": f"Added {req.ticker} to watchlist"}

@router.get("/")
def get_watchlist():
    return {"watchlist": list(watchlist)}
