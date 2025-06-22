from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.fetcher import summarize_extracted_10q_sections
import requests
import yfinance as yf

router = APIRouter()

class TickerRequest(BaseModel):
    ticker: str
    debug: bool = False  # Optional field

@router.post("/summary-by-ticker")
def summarize_by_ticker(req: TickerRequest):
    try:
        print(f"[DEBUG] Starting summary generation for {req.ticker}")
        result = summarize_extracted_10q_sections(req.ticker, debug=req.debug)
        print(f"[DEBUG] Successfully generated summary for {req.ticker}")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to generate summary for {req.ticker}: {e}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-prices")
def stock_prices(symbols: str = Query(...)):
    result = {}
    for symbol in symbols.split(','):
        try:
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            price = fast_info.get("last_price") or 0
            change = fast_info.get("last_change") or 0
            change_percent = fast_info.get("last_change_percent") or 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching {symbol}: {str(e)}")

        result[symbol.upper()] = {
            "price": price,
            "change": change,
            "changePercent": change_percent,
        }
    return result


