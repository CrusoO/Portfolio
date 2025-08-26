"""
Canvas art endpoints for saving and retrieving artwork
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.canvas import CanvasArt
from app.schemas.canvas import CanvasArtCreate, CanvasArtResponse, CanvasGalleryResponse, CanvasArtUpdate

router = APIRouter(prefix="/api/canvas", tags=["Canvas Art"])


@router.post("/save", response_model=dict)
async def save_canvas(artwork_data: CanvasArtCreate, db: Session = Depends(get_db)):
    """Save canvas artwork"""
    # Generate image URL (in production, you'd save to CDN/S3)
    image_url = f"/storage/images/artwork_{int(__import__('time').time() * 1000)}.png"
    
    artwork = CanvasArt(
        username=artwork_data.username or "Anonymous",
        title=artwork_data.title,
        image_data=artwork_data.image_data,
        image_url=image_url,
        contributors=artwork_data.contributors or [],
        is_public=artwork_data.is_public if artwork_data.is_public is not None else True
    )
    
    db.add(artwork)
    db.commit()
    db.refresh(artwork)
    
    return {
        "id": f"artwork_{artwork.id}",
        "message": "Artwork saved successfully",
        "url": image_url
    }


@router.put("/save/{artwork_id}", response_model=dict)
async def update_canvas(artwork_id: str, artwork_data: CanvasArtUpdate, db: Session = Depends(get_db)):
    """Update existing canvas artwork"""
    # Handle both string and integer IDs
    if artwork_id.startswith("artwork_"):
        db_id = artwork_id.replace("artwork_", "")
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(db_id)).first()
    else:
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(artwork_id)).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Update fields if provided
    if artwork_data.title is not None:
        artwork.title = artwork_data.title
    if artwork_data.image_data is not None:
        artwork.image_data = artwork_data.image_data
    if artwork_data.contributors is not None:
        artwork.contributors = artwork_data.contributors
    if artwork_data.is_public is not None:
        artwork.is_public = artwork_data.is_public
    
    db.commit()
    db.refresh(artwork)
    
    return {
        "id": f"artwork_{artwork.id}",
        "message": "Artwork updated successfully", 
        "url": artwork.image_url
    }


@router.get("/gallery")
async def get_gallery(
    limit: int = 10, 
    offset: int = 0, 
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get artwork gallery with pagination"""
    query = db.query(CanvasArt)
    
    if is_public is not None:
        query = query.filter(CanvasArt.is_public == is_public)
    
    # Get total count
    total = query.count()
    
    # Get paginated artworks
    artworks = query.order_by(CanvasArt.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to gallery format
    gallery_artworks = []
    for artwork in artworks:
        gallery_artworks.append({
            "id": f"artwork_{artwork.id}",
            "username": artwork.username,
            "title": artwork.title,
            "image_url": artwork.image_url or f"/storage/images/artwork_{artwork.id}.png",
            "contributors": artwork.contributors or [],
            "created_at": artwork.created_at.isoformat() + 'Z',
            "is_public": artwork.is_public
        })
    
    return {
        "artworks": gallery_artworks,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/save/{artwork_id}", response_model=dict)
async def get_artwork_for_editing(artwork_id: str, db: Session = Depends(get_db)):
    """Get specific artwork by ID for editing (includes full image_data)"""
    # Handle both string and integer IDs
    if artwork_id.startswith("artwork_"):
        db_id = artwork_id.replace("artwork_", "")
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(db_id)).first()
    else:
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(artwork_id)).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    return {
        "id": f"artwork_{artwork.id}",
        "username": artwork.username,
        "title": artwork.title,
        "image_data": artwork.image_data,
        "contributors": artwork.contributors or [],
        "created_at": artwork.created_at.isoformat() + 'Z',
        "updated_at": artwork.updated_at.isoformat() + 'Z' if artwork.updated_at else artwork.created_at.isoformat() + 'Z',
        "is_public": artwork.is_public
    }


@router.delete("/delete/{artwork_id}")
async def delete_artwork(artwork_id: str, db: Session = Depends(get_db)):
    """Delete artwork"""
    # Handle both string and integer IDs
    if artwork_id.startswith("artwork_"):
        db_id = artwork_id.replace("artwork_", "")
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(db_id)).first()
    else:
        artwork = db.query(CanvasArt).filter(CanvasArt.id == int(artwork_id)).first()
    
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    db.delete(artwork)
    db.commit()
    
    return {"message": "Artwork deleted successfully"}