from fastapi import APIRouter
from pydantic import BaseModel
from app.services.summarizer import summarize_transcript

router = APIRouter()

class SummaryRequest(BaseModel):
    ticker: str
    transcript_text: str

class SummaryResponse(BaseModel):
    ticker: str
    summary: str

@router.post("/", response_model=SummaryResponse)
async def summarize(req: SummaryRequest):
    summary = summarize_transcript(req.transcript_text, req.ticker)
    return SummaryResponse(ticker=req.ticker, summary=summary)
