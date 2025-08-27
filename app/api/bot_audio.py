"""
Bot Audio endpoints for search and upload functionality
"""
import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.core.database import get_db
from app.core.security import get_admin_user
from app.core.config import settings
from app.models.bot_voice import BotVoice
from app.models.user import User
from app.schemas.bot_voice import (
    BotVoiceSearchRequest,
    BotVoiceSearchResponse,
    BotVoiceUploadResponse,
    BotVoiceListResponse,
    BotVoiceUpdateRequest,
    BotVoiceDeleteResponse
)

router = APIRouter(prefix="/api/audio/bot", tags=["Bot Audio"])

# Ensure upload directory exists
UPLOAD_DIR = "uploads/bot_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed audio file types
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", 
    "audio/m4a", "audio/webm", "audio/aac"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/search", response_model=BotVoiceSearchResponse)
async def search_bot_audio(request: BotVoiceSearchRequest, db: Session = Depends(get_db)):
    """Search for bot audio files based on trigger text"""
    try:
        search_text = request.searchText.lower().strip()
        
        # Build search query
        query = db.query(BotVoice).filter(
            BotVoice.is_active == True,
            BotVoice.priority >= request.min_priority,
            or_(
                BotVoice.trigger_text.ilike(f"%{search_text}%"),
                BotVoice.title.ilike(f"%{search_text}%")
            )
        ).order_by(desc(BotVoice.priority), BotVoice.created_at)
        
        # Get total count
        total_found = query.count()
        
        # Apply limit
        results = query.limit(request.limit).all()
        
        return BotVoiceSearchResponse(
            success=True,
            results=results,
            total_found=total_found,
            search_text=search_text
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/upload", response_model=BotVoiceUploadResponse)
async def upload_bot_audio(
    audio: UploadFile = File(...),
    title: str = Form(...),
    trigger_text: str = Form(...),
    priority: int = Form(5),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Upload a new bot audio file"""
    
    # Validate file type
    if audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_AUDIO_TYPES)}"
        )
    
    # Check file size
    audio_content = await audio.read()
    if len(audio_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(audio.filename)[1].lower()
        if not file_extension:
            file_extension = ".mp3"  # Default extension
            
        unique_filename = f"bot_audio_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(audio_content)
        
        # Create database record
        bot_voice = BotVoice(
            title=title.strip(),
            trigger_text=trigger_text.strip(),
            audio_url=f"/uploads/bot_audio/{unique_filename}",
            audio_filename=audio.filename,
            priority=max(1, min(10, priority)),  # Ensure priority is 1-10
            is_active=is_active,
            file_size=len(audio_content),
            content_type=audio.content_type,
            created_by=admin_user.username
        )
        
        db.add(bot_voice)
        db.commit()
        db.refresh(bot_voice)
        
        return BotVoiceUploadResponse(
            success=True,
            message="Bot audio uploaded successfully",
            bot_voice_id=bot_voice.id,
            audio_url=bot_voice.audio_url
        )
        
    except Exception as e:
        # Clean up file if database save fails
        if os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/list", response_model=BotVoiceListResponse)
async def list_bot_audio(
    limit: int = 50,
    offset: int = 0,
    active_only: bool = True,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Get list of all bot audio files (admin only)"""
    
    query = db.query(BotVoice)
    
    if active_only:
        query = query.filter(BotVoice.is_active == True)
    
    query = query.order_by(desc(BotVoice.priority), BotVoice.created_at)
    
    total = query.count()
    results = query.offset(offset).limit(limit).all()
    
    return BotVoiceListResponse(
        success=True,
        bot_voices=results,
        total=total
    )


@router.put("/{bot_voice_id}", response_model=BotVoiceUploadResponse)
async def update_bot_audio(
    bot_voice_id: int,
    update_data: BotVoiceUpdateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update bot audio metadata"""
    
    bot_voice = db.query(BotVoice).filter(BotVoice.id == bot_voice_id).first()
    if not bot_voice:
        raise HTTPException(status_code=404, detail="Bot audio not found")
    
    # Update fields if provided
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if hasattr(bot_voice, field):
            setattr(bot_voice, field, value)
    
    db.commit()
    db.refresh(bot_voice)
    
    return BotVoiceUploadResponse(
        success=True,
        message="Bot audio updated successfully",
        bot_voice_id=bot_voice.id,
        audio_url=bot_voice.audio_url
    )


@router.delete("/{bot_voice_id}", response_model=BotVoiceDeleteResponse)
async def delete_bot_audio(
    bot_voice_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete bot audio file"""
    
    bot_voice = db.query(BotVoice).filter(BotVoice.id == bot_voice_id).first()
    if not bot_voice:
        raise HTTPException(status_code=404, detail="Bot audio not found")
    
    # Delete physical file
    if bot_voice.audio_url.startswith("/uploads/"):
        file_path = bot_voice.audio_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Delete database record
    db.delete(bot_voice)
    db.commit()
    
    return BotVoiceDeleteResponse(
        success=True,
        message="Bot audio deleted successfully"
    )


@router.get("/play/{bot_voice_id}")
async def play_bot_audio(bot_voice_id: int, db: Session = Depends(get_db)):
    """Stream bot audio file"""
    
    bot_voice = db.query(BotVoice).filter(
        BotVoice.id == bot_voice_id,
        BotVoice.is_active == True
    ).first()
    
    if not bot_voice:
        raise HTTPException(status_code=404, detail="Bot audio not found")
    
    file_path = bot_voice.audio_url.lstrip("/")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
    
    return FileResponse(
        path=file_path,
        media_type=bot_voice.content_type,
        filename=bot_voice.audio_filename,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600"
        }
    )
