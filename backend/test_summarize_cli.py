import requests
import argparse
import json
from pathlib import Path

def main(ticker: str, transcript_path: str, host: str):
    # Read transcript text
    transcript_file = Path(transcript_path)
    if not transcript_file.exists():
        print(f"Transcript file not found: {transcript_path}")
        return

    with open(transcript_file, "r") as f:
        transcript = f.read()

    # Prepare and send POST request
    payload = {
        "ticker": ticker,
        "transcript_text": transcript
    }

    try:
        res = requests.post(f"{host}/summarize", json=payload)
        res.raise_for_status()
        print("\n✅ Summary Response:")
        print(json.dumps(res.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if e.response is not None:
            print("Response body:")
            print(e.response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test /summarize endpoint with a local transcript.")
    parser.add_argument("--ticker", type=str, default="TECH", help="Stock ticker symbol")
    parser.add_argument("--file", type=str, default="testable_transcript_cleaned.txt", help="Path to transcript file")
    parser.add_argument("--host", type=str, default="http://127.0.0.1:8000", help="FastAPI host URL")

    args = parser.parse_args()
    main(args.ticker, args.file, args.host)
