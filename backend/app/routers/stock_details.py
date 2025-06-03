from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import yfinance as yf
from ..firebase_config import verify_token
from ..services.fetcher import summarize_extracted_10q_sections

router = APIRouter()

@router.get("/stock/{ticker}")
async def get_stock_details(ticker: str, current_user: Dict[str, Any] = Depends(verify_token)):
    try:
        # Fetch stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get basic price data
        price_data = {
            "price": info.get("currentPrice", 0),
            "change": info.get("regularMarketChange", 0),
            "changePercent": info.get("regularMarketChangePercent", 0),
            "marketCap": info.get("marketCap", 0),
            "peRatio": info.get("trailingPE", 0),
            "eps": info.get("trailingEps", 0),
            "volume": info.get("regularMarketVolume", 0),
        }
        
        # Get AI summary
        try:
            summary_result = summarize_extracted_10q_sections(ticker)
            price_data["summary"] = summary_result.get("summary", "No summary available.")
        except Exception as e:
            price_data["summary"] = "Unable to fetch AI summary at this time."
        
        return price_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch details for {ticker}") 