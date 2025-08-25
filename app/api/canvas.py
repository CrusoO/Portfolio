"""
Canvas art endpoints for saving and retrieving artwork
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.canvas import CanvasArt
from app.schemas.canvas import CanvasArtCreate, CanvasArtResponse

router = APIRouter(prefix="/api/canvas", tags=["Canvas Art"])


@router.post("/save", response_model=dict)
async def save_canvas(artwork_data: CanvasArtCreate, db: Session = Depends(get_db)):
    """Save canvas artwork"""
    artwork = CanvasArt(
        username=artwork_data.username,
        title=artwork_data.title,
        image_data=artwork_data.image_data
    )
    
    db.add(artwork)
    db.commit()
    db.refresh(artwork)
    
    return {"message": "Artwork saved!", "id": artwork.id}


@router.get("", response_model=List[CanvasArtResponse])
async def get_artworks(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent artworks"""
    artworks = db.query(CanvasArt).order_by(CanvasArt.created_at.desc()).limit(limit).all()
    return artworks


@router.get("/{artwork_id}", response_model=CanvasArtResponse)
async def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Get specific artwork by ID"""
    artwork = db.query(CanvasArt).filter(CanvasArt.id == artwork_id).first()
    
    if not artwork:
        return {"message": "Artwork not found"}
    
    return artwork


@router.delete("/{artwork_id}")
async def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Delete artwork"""
    artwork = db.query(CanvasArt).filter(CanvasArt.id == artwork_id).first()
    
    if not artwork:
        return {"message": "Artwork not found"}
    
    db.delete(artwork)
    db.commit()
    
    return {"message": "Artwork deleted successfully"}
