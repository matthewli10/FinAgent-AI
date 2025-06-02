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
        result = summarize_extracted_10q_sections(req.ticker, debug=req.debug)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-prices")
def stock_prices(symbols: str = Query(...)):
    result = {}
    for symbol in symbols.split(','):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice')
        change = info.get('regularMarketChange')
        change_percent = info.get('regularMarketChangePercent')
        result[symbol.upper()] = {
            'price': price,
            'change': change,
            'changePercent': change_percent,
        }
    return result

