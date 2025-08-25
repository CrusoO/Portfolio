"""
Review schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    message: str
    rating: float = 5.0


class ReviewCreate(ReviewBase):
    username: Optional[str] = "Anonymous"


class ReviewResponse(ReviewBase):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float
