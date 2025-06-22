import os
import requests
from app.services.summarizer import summarize_transcript
from dotenv import load_dotenv
from app.models import Summary
from app.database import SessionLocal
from datetime import date, datetime

# Load environment variables
load_dotenv()

# Debug environment variables
SEC_API_KEY = os.getenv("SEC_API_KEY")
EXTRACTOR_API = "https://api.sec-api.io/extractor"
CIK_LOOKUP_URL = "https://www.sec.gov/include/ticker.txt"
EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {"User-Agent": "YourAppName/1.0"}

# Most important 10-Q sections for investors
IMPORTANT_10Q_ITEMS = [
    "part1item2",   # Management's Discussion and Analysis
    "part1item1",   # Financial Statements
    "part2item1a",  # Risk Factors
    "part1item3",   # Market Risk
    "part1item4"    # Controls and Procedures
]

def get_cik_from_ticker(ticker: str) -> str:
    response = requests.get(CIK_LOOKUP_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception("Failed to fetch CIK mapping")
    lines = response.text.splitlines()
    mapping = {line.split('\t')[0].upper(): line.split('\t')[1].zfill(10) for line in lines}
    return mapping.get(ticker.upper())

def get_latest_10q_filing_url(ticker: str) -> str:
    cik = get_cik_from_ticker(ticker)
    if not cik:
        raise Exception(f"CIK not found for ticker {ticker}")

    url = EDGAR_SUBMISSIONS_URL.format(cik=cik)
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception("Failed to fetch filings from SEC")

    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    for i, form in enumerate(filings.get("form", [])):
        if form == "10-Q":
            accession = filings["accessionNumber"][i].replace("-", "")
            primary_doc = filings["primaryDocument"][i]
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"

    raise Exception(f"No recent 10-Q found for ticker {ticker}")

def get_latest_10q_filing_info(ticker: str):
    cik = get_cik_from_ticker(ticker)
    if not cik:
        raise Exception(f"CIK not found for ticker {ticker}")

    url = EDGAR_SUBMISSIONS_URL.format(cik=cik)
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception("Failed to fetch filings from SEC")

    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    for i, form in enumerate(filings.get("form", [])):
        if form == "10-Q":
            accession = filings["accessionNumber"][i].replace("-", "")
            primary_doc = filings["primaryDocument"][i]
            filing_date = filings["filingDate"][i]  # YYYY-MM-DD
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
            return filing_url, filing_date
    raise Exception(f"No recent 10-Q found for ticker {ticker}")

def extract_filing_section(filing_url: str, item_code: str, return_type: str = "text") -> str:
    params = {
        "url": filing_url,
        "item": item_code,
        "type": return_type,
        "token": SEC_API_KEY
    }
    response = requests.get(EXTRACTOR_API, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to extract section {item_code}. Status: {response.status_code}")
    
    # Handle different response types
    try:
        content = response.text
        # If the response is JSON, try to extract the text content
        if content.strip().startswith('{'):
            import json
            json_response = json.loads(content)
            # Handle different possible JSON structures
            if isinstance(json_response, dict):
                if 'text' in json_response:
                    content = json_response['text']
                elif 'content' in json_response:
                    content = json_response['content']
                elif 'data' in json_response:
                    content = json_response['data']
                else:
                    # If we can't find the content, convert the whole thing to string
                    content = str(json_response)
        
        # Ensure we return a string
        if not isinstance(content, str):
            content = str(content)
            
        return content
    except Exception as e:
        print(f"[DEBUG] Error processing response for {item_code}: {e}")
        return f"Error: Failed to process section {item_code} - {str(e)}"

def fetch_all_important_sections(ticker: str, filing_url: str) -> dict:
    sections = {}
    for item_code in IMPORTANT_10Q_ITEMS:
        try:
            content = extract_filing_section(filing_url, item_code)
            # Ensure content is a string and handle any remaining issues
            if not isinstance(content, str):
                content = str(content)
            sections[item_code] = content
        except Exception as e:
            print(f"[DEBUG] Error fetching section {item_code} for {ticker}: {e}")
            sections[item_code] = f"Error: {str(e)}"
    return {
        "ticker": ticker.upper(),
        "filing_url": filing_url,
        "sections": sections
    }

def summarize_extracted_10q_sections(ticker: str, debug: bool = False) -> dict:
    filing_url = get_latest_10q_filing_url(ticker)
    result = fetch_all_important_sections(ticker, filing_url)

    combined_text = "\n\n".join([
        f"## Section: {code}\n{content}"
        for code, content in result["sections"].items()
        if isinstance(content, str) and not content.startswith("Error:")
    ])

    if not combined_text.strip():
        combined_text = "No valid sections found for analysis."

    summary = summarize_transcript(combined_text, ticker)

    if debug:
        return {
            "ticker": ticker.upper(),
            "filing_url": filing_url,
            "sections": result["sections"],
            "combined_text": combined_text,
            "summary": summary
        }

    return {
        "ticker": ticker.upper(),
        "summary": summary
    }

def get_summary_from_db(ticker: str, filing_date: date):
    print(f"[DEBUG] Checking DB for summary: ticker={ticker}, filing_date={filing_date}")
    db = SessionLocal()
    try:
        summary = db.query(Summary).filter_by(ticker=ticker, filing_date=filing_date).first()
        if summary:
            print(f"[DEBUG] Found summary in DB: {summary.summary_text[:50]}...")
        else:
            print(f"[DEBUG] No summary found in DB")
        return summary
    except Exception as e:
        print(f"[DEBUG] Error querying DB: {e}")
        return None
    finally:
        db.close()

def create_summary_placeholder(ticker: str, filing_date: date):
    print(f"[DEBUG] Creating placeholder for: ticker={ticker}, filing_date={filing_date}")
    db = SessionLocal()
    try:
        placeholder = Summary(
            ticker=ticker,
            filing_date=filing_date,
            summary_text="generating...",
            created_at=datetime.utcnow()
        )
        db.add(placeholder)
        db.commit()
        print(f"[DEBUG] Placeholder created successfully")
    except Exception as e:
        print(f"[DEBUG] Error creating placeholder: {e}")
        db.rollback()
    finally:
        db.close()

def update_summary_in_db(ticker: str, filing_date: date, summary_text: str):
    print(f"[DEBUG] Updating summary in DB: ticker={ticker}, filing_date={filing_date}")
    db = SessionLocal()
    try:
        summary_to_update = db.query(Summary).filter_by(ticker=ticker, filing_date=filing_date).first()
        if summary_to_update:
            summary_to_update.summary_text = summary_text
            db.commit()
            print(f"[DEBUG] Summary updated successfully")
        else:
            print(f"[DEBUG] No summary found to update")
    except Exception as e:
        print(f"[DEBUG] Error updating summary: {e}")
        db.rollback()
    finally:
        db.close()

def run_ai_summary_and_save(ticker: str, filing_date: date):
    """
    This function runs the slow AI summarization and updates the DB.
    It's designed to be called as a background task.
    """
    print(f"[BACKGROUND TASK STARTED] Starting AI summary for {ticker} ({filing_date})...")
    try:
        # Re-fetch filing_url as it's not passed to the background task
        print(f"[BACKGROUND TASK] Getting filing info for {ticker}")
        filing_url, _ = get_latest_10q_filing_info(ticker)
        print(f"[BACKGROUND TASK] Filing URL: {filing_url}")
        
        print(f"[BACKGROUND TASK] Fetching sections for {ticker}")
        result = fetch_all_important_sections(ticker, filing_url)
        sections = result["sections"]  # Extract the actual sections dict
        
        # Debug: Check what we're working with
        print(f"[DEBUG] Sections for {ticker}: {list(sections.keys())}")
        for code, content in sections.items():
            print(f"[DEBUG] Section {code} type: {type(content)}, length: {len(str(content))}")
            if not isinstance(content, str):
                print(f"[DEBUG] Section {code} is not string: {content}")
        
        print(f"[BACKGROUND TASK] Processing sections for {ticker}")
        combined_text = "\n\n".join([
            f"## Section: {code}\n{content}"
            for code, content in sections.items()
            if isinstance(content, str) and not content.startswith("Error:")
        ])
        
        if not combined_text.strip():
            combined_text = "No valid sections found for analysis."
            
        print(f"[BACKGROUND TASK] Calling AI summarizer for {ticker}")
        summary_text = summarize_transcript(combined_text, ticker)
        print(f"[BACKGROUND TASK] AI summary generated for {ticker}")
        
        print(f"[BACKGROUND TASK] Saving to database for {ticker}")
        update_summary_in_db(ticker, filing_date, summary_text)
        print(f"[Background Task] Successfully generated and saved summary for {ticker}.")
    except Exception as e:
        print(f"[Background Task ERROR] Failed to generate summary for {ticker}: {e}")
        import traceback
        print(f"[Background Task ERROR] Full traceback: {traceback.format_exc()}")
        error_message = f"Error generating summary: {str(e)}"
        update_summary_in_db(ticker, filing_date, error_message)

