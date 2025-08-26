"""
Canvas art schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class CanvasArtBase(BaseModel):
    title: str = "Untitled"
    image_data: str  # Base64 encoded image


class CanvasArtCreate(CanvasArtBase):
    username: Optional[str] = "Anonymous"
    contributors: Optional[List[Any]] = []
    is_public: Optional[bool] = True


class CanvasArtResponse(CanvasArtBase):
    id: int
    username: str
    image_url: Optional[str] = None
    contributors: List[Any] = []
    is_public: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


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
    contributors: Optional[List[Any]] = None
    is_public: Optional[bool] = None

