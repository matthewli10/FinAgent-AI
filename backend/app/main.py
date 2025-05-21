from fastapi import FastAPI
from app.routers import summarize, watchlist, fetch
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Earnings Summary Agent")

app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(fetch.router, prefix="/fetch", tags=["Fetch"])
