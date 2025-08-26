"""
Audio processing endpoints for TTS caching and custom audio management
"""
import os
import hashlib
import aiofiles
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.core.config import settings
from app.models.audio import AudioCache, CustomAudio
from app.models.user import User
from app.schemas.audio import (
    TTSRequest, TTSResponse, CustomAudioCreate, CustomAudioResponse, 
    CustomAudioUpdate, AudioSearchRequest, CacheStatsResponse, AudioCacheResponse
)
from app.core.security import get_current_user
from app.services.audio_service import AudioService

router = APIRouter(prefix="/api/audio", tags=["Audio"])


# Initialize audio service
audio_service = AudioService()


@router.post("/tts", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    db: Session = Depends(get_db)
):
    """Generate TTS audio with caching"""
    try:
        # Generate text hash for caching
        text_hash = hashlib.md5(
            f"{request.text}-{request.voice_id}-{str(request.voice_settings)}".encode()
        ).hexdigest()
        
        # Check cache first if requested
        if request.use_cache:
            cached_audio = db.query(AudioCache).filter(
                AudioCache.text_hash == text_hash
            ).first()
            
            if cached_audio:
                # Update last used timestamp
                cached_audio.last_used = datetime.utcnow()
                db.commit()
                
                return TTSResponse(
                    audio_url=cached_audio.audio_url,
                    text_hash=text_hash,
                    cached=True,
                    file_size=cached_audio.file_size,
                    duration=cached_audio.duration,
                    voice_id=cached_audio.voice_id
                )
        
        # Generate new audio using ElevenLabs
        audio_data = await audio_service.generate_tts(
            text=request.text,
            voice_id=request.voice_id or settings.DEFAULT_VOICE_ID,
            voice_settings=request.voice_settings
        )
        
        # Save audio file
        filename = f"tts_{text_hash}.mp3"
        file_path = os.path.join(settings.AUDIO_DIR, filename)
        
        # Ensure directory exists
        os.makedirs(settings.AUDIO_DIR, exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(audio_data)
        
        file_size = len(audio_data)
        audio_url = f"/storage/audio/{filename}"
        
        # Cache the audio
        if request.use_cache:
            cache_entry = AudioCache(
                text=request.text,
                text_hash=text_hash,
                voice_id=request.voice_id or settings.DEFAULT_VOICE_ID,
                voice_settings=request.voice_settings,
                audio_url=audio_url,
                file_name=filename,
                file_size=file_size,
                source="generated"
            )
            db.add(cache_entry)
            db.commit()
        
        return TTSResponse(
            audio_url=audio_url,
            text_hash=text_hash,
            cached=False,
            file_size=file_size,
            voice_id=request.voice_id or settings.DEFAULT_VOICE_ID
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate TTS: {str(e)}"
        )


@router.get("/cache/{text_hash}", response_model=AudioCacheResponse)
async def get_cached_audio(
    text_hash: str,
    db: Session = Depends(get_db)
):
    """Get cached audio by text hash"""
    cached_audio = db.query(AudioCache).filter(
        AudioCache.text_hash == text_hash
    ).first()
    
    if not cached_audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cached audio not found"
        )
    
    # Update last used timestamp
    cached_audio.last_used = datetime.utcnow()
    db.commit()
    
    return cached_audio


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audio cache statistics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Calculate statistics
    total_cached = db.query(func.count(AudioCache.id)).scalar()
    total_size = db.query(func.sum(AudioCache.file_size)).scalar() or 0
    unique_voices = db.query(func.count(func.distinct(AudioCache.voice_id))).scalar()
    
    oldest_entry = db.query(func.min(AudioCache.created_at)).scalar()
    newest_entry = db.query(func.max(AudioCache.created_at)).scalar()
    
    # Usage in last week
    week_ago = datetime.utcnow() - timedelta(days=7)
    used_last_week = db.query(func.count(AudioCache.id)).filter(
        AudioCache.last_used >= week_ago
    ).scalar()
    
    return CacheStatsResponse(
        total_cached=total_cached,
        total_size_bytes=total_size,
        unique_voices=unique_voices,
        oldest_entry=oldest_entry,
        newest_entry=newest_entry,
        used_last_week=used_last_week
    )


@router.delete("/cache/cleanup")
async def cleanup_cache(
    days_old: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up old cache entries (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    # Get files to delete
    old_entries = db.query(AudioCache).filter(
        AudioCache.last_used < cutoff_date
    ).all()
    
    deleted_files = 0
    for entry in old_entries:
        try:
            file_path = os.path.join(settings.AUDIO_DIR, entry.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files += 1
        except Exception as e:
            print(f"Error deleting file {entry.file_name}: {e}")
    
    # Delete from database
    deleted_count = db.query(AudioCache).filter(
        AudioCache.last_used < cutoff_date
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Cache cleanup completed",
        "deleted_entries": deleted_count,
        "deleted_files": deleted_files
    }


@router.post("/custom", response_model=CustomAudioResponse)
async def upload_custom_audio(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    note_id: Optional[int] = Form(None),
    text_content: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload custom audio file (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_AUDIO_TYPES)}"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large"
        )
    
    # Generate unique filename
    timestamp = int(datetime.utcnow().timestamp())
    filename = f"custom_{timestamp}_{file.filename}"
    file_path = os.path.join(settings.AUDIO_DIR, filename)
    
    # Ensure directory exists
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Create database record
    custom_audio = CustomAudio(
        title=title,
        description=description,
        note_id=note_id,
        audio_url=f"/storage/audio/{filename}",
        file_name=filename,
        file_size=len(content),
        uploaded_by=current_user.id,
        text_content=text_content
    )
    
    db.add(custom_audio)
    db.commit()
    db.refresh(custom_audio)
    
    return custom_audio


@router.get("/custom", response_model=List[CustomAudioResponse])
async def get_custom_audio(
    note_id: Optional[int] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get custom audio files"""
    query = db.query(CustomAudio)
    
    if note_id:
        query = query.filter(CustomAudio.note_id == note_id)
    
    if active_only:
        query = query.filter(CustomAudio.is_active == True)
    
    return query.order_by(CustomAudio.uploaded_at.desc()).all()


@router.post("/custom/search", response_model=List[CustomAudioResponse])
async def search_custom_audio(
    request: AudioSearchRequest,
    db: Session = Depends(get_db)
):
    """Search custom audio files"""
    query = db.query(CustomAudio).filter(CustomAudio.is_active == True)
    
    search_term = f"%{request.query.lower()}%"
    
    if request.search_type == "title":
        query = query.filter(func.lower(CustomAudio.title).like(search_term))
    elif request.search_type == "description":
        query = query.filter(func.lower(CustomAudio.description).like(search_term))
    elif request.search_type == "content":
        query = query.filter(func.lower(CustomAudio.text_content).like(search_term))
    else:  # "all"
        query = query.filter(
            func.lower(CustomAudio.title).like(search_term) |
            func.lower(CustomAudio.description).like(search_term) |
            func.lower(CustomAudio.text_content).like(search_term)
        )
    
    return query.order_by(CustomAudio.uploaded_at.desc()).all()


@router.patch("/custom/{audio_id}", response_model=CustomAudioResponse)
async def update_custom_audio(
    audio_id: int,
    update_data: CustomAudioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update custom audio (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audio = db.query(CustomAudio).filter(CustomAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom audio not found"
        )
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(audio, field, value)
    
    db.commit()
    db.refresh(audio)
    
    return audio


@router.delete("/custom/{audio_id}")
async def delete_custom_audio(
    audio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete custom audio (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    audio = db.query(CustomAudio).filter(CustomAudio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom audio not found"
        )
    
    # Delete file
    try:
        file_path = os.path.join(settings.AUDIO_DIR, audio.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {audio.file_name}: {e}")
    
    # Delete from database
    db.delete(audio)
    db.commit()
    
    return {"message": "Custom audio deleted successfully"}
