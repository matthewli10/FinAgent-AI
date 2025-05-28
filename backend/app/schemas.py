from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    firebase_uid: str

class User(UserBase):
    id: int
    firebase_uid: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FirebaseUser(BaseModel):
    uid: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class SummaryBase(BaseModel):
    ticker: str
    summary_text: str

class SummaryCreate(SummaryBase):
    pass

class Summary(SummaryBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

class WatchlistBase(BaseModel):
    ticker: str

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int
    added_at: datetime
    user_id: int

    class Config:
        from_attributes = True 