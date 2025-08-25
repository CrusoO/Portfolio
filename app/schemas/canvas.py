"""
Canvas art schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CanvasArtBase(BaseModel):
    title: str = "Untitled"
    image_data: str  # Base64 encoded image


class CanvasArtCreate(CanvasArtBase):
    username: Optional[str] = "Anonymous"


class CanvasArtResponse(CanvasArtBase):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True
