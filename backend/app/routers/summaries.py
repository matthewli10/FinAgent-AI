from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..firebase_config import verify_token

router = APIRouter()

@router.get("/summaries", response_model=List[schemas.Summary])
async def get_summaries(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.Summary).filter(models.Summary.user_id == user.id).all()

@router.post("/summaries", response_model=schemas.Summary)
async def create_summary(
    summary: schemas.SummaryCreate,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_summary = models.Summary(**summary.dict(), user_id=user.id)
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary 