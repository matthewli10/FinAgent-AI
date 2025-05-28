import os
import requests
from app.services.summarizer import summarize_transcript
from dotenv import load_dotenv

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
    return response.text

def fetch_all_important_sections(ticker: str, filing_url: str) -> dict:
    sections = {}
    for item_code in IMPORTANT_10Q_ITEMS:
        try:
            content = extract_filing_section(filing_url, item_code)
            sections[item_code] = content
        except Exception as e:
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
        if not content.startswith("Error:")
    ])

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

