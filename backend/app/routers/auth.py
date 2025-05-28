from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..firebase_config import verify_token

router = APIRouter()

@router.post("/users", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    # Verify that the Firebase UID matches the token
    if user.firebase_uid != firebase_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Firebase UID mismatch"
        )
    
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | 
        (models.User.firebase_uid == user.firebase_uid)
    ).first()
    
    if db_user:
        return db_user  # Return existing user instead of raising error
    
    # Create new user
    db_user = models.User(
        email=user.email,
        firebase_uid=user.firebase_uid
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=schemas.User)
async def get_current_user(
    db: Session = Depends(get_db),
    firebase_user: dict = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        # If user doesn't exist in our database, create them
        db_user = models.User(
            email=firebase_user["email"],
            firebase_uid=firebase_user["uid"]
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    return user 