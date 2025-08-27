"""
Canvas art model for storing user artwork
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class CanvasArt(Base):
    __tablename__ = "canvas_art"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, default="Anonymous")
    title = Column(String(100), nullable=False, default="Untitled")
    image_data = Column(Text, nullable=False)  # Base64 encoded image data
    image_url = Column(String(1000), nullable=True)  # CDN/storage URL
    contributors = Column(JSON, nullable=False, default='[]')  # List of contributors
    is_public = Column(Boolean, nullable=False, default=True)  # Public/private flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CanvasArt(id={self.id}, title='{self.title}', username='{self.username}')>"
