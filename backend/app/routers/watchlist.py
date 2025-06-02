from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..firebase_config import verify_token

router = APIRouter()

@router.get("/watchlist", response_model=List[schemas.Watchlist])
async def get_watchlist(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        # Create user if not exists
        user = models.User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user["email"],
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == user.id).all()

@router.post("/watchlist", response_model=schemas.Watchlist)
async def add_to_watchlist(
    watchlist_item: schemas.WatchlistCreate,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        # Create user if not exists
        user = models.User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user["email"],
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # Check if ticker already exists in user's watchlist
    existing = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == user.id,
        models.Watchlist.ticker == watchlist_item.ticker
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ticker already in watchlist")
    db_watchlist = models.Watchlist(**watchlist_item.dict(), user_id=user.id)
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist

@router.delete("/watchlist/{ticker}")
async def delete_from_watchlist(
    ticker: str = Path(..., description="Ticker to remove from watchlist"),
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        user = models.User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user["email"],
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    watchlist_item = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == user.id,
        models.Watchlist.ticker == ticker.upper()
    ).first()
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Ticker not found in watchlist")
    db.delete(watchlist_item)
    db.commit()
    return {"detail": f"{ticker.upper()} removed from watchlist"}
