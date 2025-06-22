from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
import yfinance as yf
from curl_cffi import requests as cffi_requests
from ..firebase_config import verify_token
from ..services.fetcher import (
    get_latest_10q_filing_info,
    get_summary_from_db,
    create_summary_placeholder,
    run_ai_summary_and_save
)
from datetime import datetime

router = APIRouter()

@router.get("/stock/{ticker}")
async def get_stock_details(ticker: str, background_tasks: BackgroundTasks, current_user: Dict[str, Any] = Depends(verify_token)):
    print(f"[DEBUG] Starting stock details request for {ticker}")
    try:
        # --- 1. Fetch real-time price data (this is always fast) ---
        print(f"[DEBUG] Fetching price data for {ticker}")
        
        # Try with curl_cffi first, fallback to regular requests if it fails
        try:
            session = cffi_requests.Session()
            session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            session.impersonate = "chrome110"
            stock = yf.Ticker(ticker, session=session)
            info = stock.info
        except Exception as e:
            print(f"[DEBUG] curl_cffi failed for {ticker}, trying regular yfinance: {e}")
            # Fallback to regular yfinance without custom session
            stock = yf.Ticker(ticker)
            info = stock.info
        
        price_data = {
            "price": info.get("currentPrice", info.get("regularMarketPrice")),
            "change": info.get("regularMarketChange", 0),
            "changePercent": info.get("regularMarketChangePercent", 0),
            "marketCap": info.get("marketCap", 0),
            "peRatio": info.get("trailingPE", 0),
            "eps": info.get("trailingEps", 0),
            "volume": info.get("regularMarketVolume", 0),
            "summary": "loading..."
        }
        print(f"[DEBUG] Price data fetched for {ticker}")

        # --- 2. Handle the AI Summary (Asynchronously) ---
        print(f"[DEBUG] Getting filing info for {ticker}")
        filing_url, filing_date_str = get_latest_10q_filing_info(ticker)
        filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
        print(f"[DEBUG] Filing date for {ticker}: {filing_date}")
        
        print(f"[DEBUG] Checking database for existing summary")
        summary_obj = get_summary_from_db(ticker, filing_date)

        if summary_obj:
            # Case A: Summary is in the DB (either ready or still generating)
            print(f"[DEBUG] Found existing summary for {ticker}: {summary_obj.summary_text[:50]}...")
            price_data["summary"] = summary_obj.summary_text
        else:
            # Case B: No summary exists. Create a placeholder and start the background task.
            print(f"[DEBUG] No existing summary found for {ticker}, creating placeholder and starting background task")
            create_summary_placeholder(ticker, filing_date)
            background_tasks.add_task(run_ai_summary_and_save, ticker, filing_date)
            price_data["summary"] = "generating..."
            print(f"[DEBUG] Background task added for {ticker}")

        print(f"[DEBUG] Returning response for {ticker}")
        return price_data
        
    except Exception as e:
        print(f"[ERROR] Exception in get_stock_details for {ticker}: {e}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        if 'price_data' in locals() and price_data:
            price_data["summary"] = "Could not load AI summary."
            return price_data
        raise HTTPException(status_code=404, detail=f"Could not fetch details for {ticker}: {str(e)}") 