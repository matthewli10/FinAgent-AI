#!/usr/bin/env python3
"""
Script to clear error entries from the summaries table for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Summary
from datetime import date

def clear_summary_error(ticker: str, filing_date_str: str = None):
    """Clear the summary entry for a specific ticker and filing date"""
    db = SessionLocal()
    try:
        if filing_date_str:
            filing_date = date.fromisoformat(filing_date_str)
            summary = db.query(Summary).filter_by(ticker=ticker, filing_date=filing_date).first()
            
            if summary:
                print(f"Found summary for {ticker} on {filing_date}: {summary.summary_text[:100]}...")
                if "Error generating summary" in summary.summary_text:
                    print(f"Deleting error entry for {ticker}")
                    db.delete(summary)
                    db.commit()
                    print(f"Successfully deleted error entry for {ticker}")
                else:
                    print(f"Summary for {ticker} is not an error, keeping it")
            else:
                print(f"No summary found for {ticker} on {filing_date}")
        else:
            # Show all entries for the ticker
            summaries = db.query(Summary).filter_by(ticker=ticker).all()
            if summaries:
                print(f"Found {len(summaries)} summary entries for {ticker}:")
                for summary in summaries:
                    print(f"  Date: {summary.filing_date}, Content: {summary.summary_text[:100]}...")
                    if "Error generating summary" in summary.summary_text:
                        print(f"  -> Deleting error entry for {ticker} on {summary.filing_date}")
                        db.delete(summary)
                        db.commit()
                        print(f"  -> Successfully deleted error entry")
            else:
                print(f"No summary entries found for {ticker}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        filing_date = sys.argv[2] if len(sys.argv) > 2 else None
        clear_summary_error(ticker, filing_date)
    else:
        print("Usage: python clear_summary_error.py <TICKER> [FILING_DATE]")
        print("Example: python clear_summary_error.py NVDA")
        print("Example: python clear_summary_error.py NVDA 2025-05-30")
        print("Note: If no filing date is provided, all entries for the ticker will be shown") 