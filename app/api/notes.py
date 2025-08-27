"""
Notes/blog endpoints for articles and posts
"""
import os
import base64
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from elevenlabs import generate, set_api_key, Voice, VoiceSettings
import io

from app.core.database import get_db
from app.core.security import get_admin_user
from app.core.config import settings
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.schemas.voice import VoiceNoteCreate, VoiceNoteResponse, VoiceNoteUpdate

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("", response_model=List[NoteListResponse])
async def get_notes(
    published_only: bool = True,
    category: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get published notes/articles"""
    query = db.query(Note)
    
    if published_only:
        query = query.filter(Note.is_published == "published")
    
    if category:
        query = query.filter(Note.category == category)
    
    notes = query.order_by(Note.created_at.desc()).limit(limit).all()
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get specific note by ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Only return published notes unless admin
    if note.is_published != "published":
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note


@router.post("", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create new note (admin only)"""
    note = Note(
        title=note_data.title,
        content=note_data.content,
        snippet=note_data.snippet,
        category=note_data.category,
        tags=note_data.tags,
        read_time=note_data.read_time,
        is_published=note_data.is_published
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update note (admin only)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update fields if provided
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.snippet is not None:
        note.snippet = note_data.snippet
    if note_data.category is not None:
        note.category = note_data.category
    if note_data.tags is not None:
        note.tags = note_data.tags
    if note_data.read_time is not None:
        note.read_time = note_data.read_time
    if note_data.is_published is not None:
        note.is_published = note_data.is_published
    
    db.commit()
    db.refresh(note)
    
    return note


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete note (admin only)"""
    note = db.query(Note).filter(Note.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}


# Voice Note Endpoints

@router.post("/{note_id}/voice", response_model=VoiceNoteResponse)
async def create_voice_note(
    note_id: int,
    voice_data: VoiceNoteCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Create voice note for a specific note (admin only)"""
    
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="ElevenLabs API key not configured"
        )
    
    # Find the note
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    try:
        # Set ElevenLabs API key
        set_api_key(settings.ELEVENLABS_API_KEY)
        
        # Use provided voice_id or default
        voice_id = voice_data.voice_id or settings.ELEVENLABS_VOICE_ID
        
        # Create voice settings
        voice_settings = VoiceSettings(
            stability=voice_data.stability,
            similarity_boost=voice_data.similarity_boost,
            style=voice_data.style,
            use_speaker_boost=voice_data.use_speaker_boost
        )
        
        # Generate audio
        audio = generate(
            text=voice_data.voice_text,
            voice=Voice(voice_id=voice_id, settings=voice_settings),
            model="eleven_multilingual_v2"
        )
        
        # Create uploads directory if it doesn't exist
        voice_dir = os.path.join(settings.UPLOAD_DIR, "voices")
        os.makedirs(voice_dir, exist_ok=True)
        
        # Save audio file
        voice_filename = f"note_{note_id}_voice.mp3"
        voice_file_path = os.path.join(voice_dir, voice_filename)
        
        with open(voice_file_path, "wb") as f:
            f.write(audio)
        
        # Calculate audio duration (approximate)
        audio_duration = len(audio) // 16000  # Rough estimate
        
        # Update note with voice information
        note.has_voice_note = "true"
        note.voice_file_path = voice_file_path
        note.voice_transcript = voice_data.voice_text
        note.voice_duration = audio_duration
        
        db.commit()
        db.refresh(note)
        
        return VoiceNoteResponse(
            success=True,
            message="Voice note created successfully",
            note_id=note_id,
            voice_file_path=voice_file_path,
            voice_duration=audio_duration
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create voice note: {str(e)}"
        )


@router.get("/{note_id}/voice/play")
async def play_voice_note(note_id: int, db: Session = Depends(get_db)):
    """Play voice note for a specific note"""
    
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.has_voice_note != "true" or not note.voice_file_path:
        raise HTTPException(status_code=404, detail="No voice note found for this note")
    
    if not os.path.exists(note.voice_file_path):
        raise HTTPException(status_code=404, detail="Voice file not found")
    
    return FileResponse(
        path=note.voice_file_path,
        media_type="audio/mpeg",
        filename=f"note_{note_id}_voice.mp3"
    )


@router.put("/{note_id}/voice", response_model=VoiceNoteResponse)
async def update_voice_note(
    note_id: int,
    voice_data: VoiceNoteUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update voice note for a specific note (admin only)"""
    
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="ElevenLabs API key not configured"
        )
    
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.has_voice_note != "true":
        raise HTTPException(status_code=404, detail="No voice note exists for this note")
    
    # If no voice_text provided, don't regenerate
    if not voice_data.voice_text:
        return VoiceNoteResponse(
            success=True,
            message="No changes made - voice text not provided",
            note_id=note_id,
            voice_file_path=note.voice_file_path,
            voice_duration=note.voice_duration
        )
    
    try:
        set_api_key(settings.ELEVENLABS_API_KEY)
        
        voice_id = voice_data.voice_id or settings.ELEVENLABS_VOICE_ID
        
        voice_settings = VoiceSettings(
            stability=voice_data.stability or 0.5,
            similarity_boost=voice_data.similarity_boost or 0.75,
            style=voice_data.style or 0.0,
            use_speaker_boost=voice_data.use_speaker_boost or True
        )
        
        # Generate new audio
        audio = generate(
            text=voice_data.voice_text,
            voice=Voice(voice_id=voice_id, settings=voice_settings),
            model="eleven_multilingual_v2"
        )
        
        # Update existing file
        if note.voice_file_path and os.path.exists(note.voice_file_path):
            with open(note.voice_file_path, "wb") as f:
                f.write(audio)
        else:
            # Create new file
            voice_dir = os.path.join(settings.UPLOAD_DIR, "voices")
            os.makedirs(voice_dir, exist_ok=True)
            voice_filename = f"note_{note_id}_voice.mp3"
            voice_file_path = os.path.join(voice_dir, voice_filename)
            
            with open(voice_file_path, "wb") as f:
                f.write(audio)
            
            note.voice_file_path = voice_file_path
        
        # Update note
        audio_duration = len(audio) // 16000
        note.voice_transcript = voice_data.voice_text
        note.voice_duration = audio_duration
        
        db.commit()
        db.refresh(note)
        
        return VoiceNoteResponse(
            success=True,
            message="Voice note updated successfully",
            note_id=note_id,
            voice_file_path=note.voice_file_path,
            voice_duration=audio_duration
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update voice note: {str(e)}"
        )


@router.delete("/{note_id}/voice")
async def delete_voice_note(
    note_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete voice note for a specific note (admin only)"""
    
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note.has_voice_note != "true":
        raise HTTPException(status_code=404, detail="No voice note exists for this note")
    
    # Delete physical file
    if note.voice_file_path and os.path.exists(note.voice_file_path):
        try:
            os.remove(note.voice_file_path)
        except Exception as e:
            print(f"Error deleting voice file: {e}")
    
    # Update note
    note.has_voice_note = "false"
    note.voice_file_path = None
    note.voice_transcript = None
    note.voice_duration = None
    
    db.commit()
    
    return {"message": "Voice note deleted successfully"}
