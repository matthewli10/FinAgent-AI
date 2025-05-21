from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.fetcher import summarize_extracted_10q_sections

router = APIRouter()

class TickerRequest(BaseModel):
    ticker: str
    debug: bool = False  # Optional field

@router.post("/summary-by-ticker")
def summarize_by_ticker(req: TickerRequest):
    try:
        result = summarize_extracted_10q_sections(req.ticker, debug=req.debug)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

