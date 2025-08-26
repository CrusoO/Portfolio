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


class CanvasGalleryArtwork(BaseModel):
    id: str
    username: str
    title: str
    image_url: str
    contributors: List[Any] = []
    created_at: str
    is_public: bool

class CanvasGalleryResponse(BaseModel):
    artworks: List[CanvasGalleryArtwork]
    total: int
    limit: int
    offset: int


class CanvasArtUpdate(BaseModel):
    title: Optional[str] = None
    image_data: Optional[str] = None
    contributors: Optional[List[Contributor]] = None
    is_public: Optional[bool] = None

