"""
Review endpoints for user feedback
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewStats

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("", response_model=dict)
async def submit_review(review_data: ReviewCreate, db: Session = Depends(get_db)):
    """Submit a new review"""
    review = Review(
        username=review_data.username,
        message=review_data.message,
        rating=review_data.rating
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return {"message": "Review submitted successfully!", "review_id": review.id}


@router.get("", response_model=List[ReviewResponse])
async def get_reviews(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent reviews"""
    reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit).all()
    return reviews


@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(db: Session = Depends(get_db)):
    """Get review statistics"""
    total_reviews = db.query(Review).count()
    
    if total_reviews == 0:
        return ReviewStats(total_reviews=0, average_rating=5.0)
    
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 5.0
    
    return ReviewStats(
        total_reviews=total_reviews,
        average_rating=round(avg_rating, 1)
    )


@router.delete("/{review_id}")
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review (admin only in production)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        return {"message": "Review not found"}
    
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}
