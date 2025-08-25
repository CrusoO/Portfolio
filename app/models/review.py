"""
Review model for user feedback and ratings
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, default="Anonymous")
    message = Column(Text, nullable=False)
    rating = Column(Float, nullable=False, default=5.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Review(id={self.id}, username='{self.username}', rating={self.rating})>"
