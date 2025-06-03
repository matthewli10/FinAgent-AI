from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import yfinance as yf
from ..firebase_config import verify_token
from ..services.fetcher import (
    summarize_extracted_10q_sections,
    get_latest_10q_filing_info,
    get_summary_from_db,
    save_summary_to_db
)
from datetime import datetime

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
        
        # Get filing information
        filing_url, filing_date_str = get_latest_10q_filing_info(ticker)
        filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
        print(f"[DEBUG] Checking DB for summary: ticker={ticker}, filing_date={filing_date}")
        summary_obj = get_summary_from_db(ticker, filing_date)
        if summary_obj:
            print("[DEBUG] Summary found in DB, returning cached summary.")
            summary_text = summary_obj.summary_text
        else:
            print("[DEBUG] Summary not found, running AI summarizer and saving to DB.")
            summary_result = summarize_extracted_10q_sections(ticker)
            summary_text = summary_result.get("summary", "No summary available.")
            save_summary_to_db(ticker, filing_date, summary_text)
        price_data["summary"] = summary_text
        
        return price_data
    except Exception as e:
        print(f"[ERROR] Exception in get_stock_details: {e}")
        raise HTTPException(status_code=404, detail=f"Could not fetch details for {ticker}") 