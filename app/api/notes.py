"""
Notes/blog endpoints for articles and posts
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse

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
