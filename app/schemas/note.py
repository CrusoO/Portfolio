"""
Note schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    content: str
    snippet: Optional[str] = None
    category: str = "General"
    tags: Optional[List[str]] = None
    read_time: int = 5
    has_voice_note: str = "false"
    voice_transcript: Optional[str] = None
    voice_duration: Optional[int] = None


class NoteCreate(NoteBase):
    is_published: str = "draft"


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    snippet: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    read_time: Optional[int] = None
    is_published: Optional[str] = None
    has_voice_note: Optional[str] = None
    voice_transcript: Optional[str] = None
    voice_duration: Optional[int] = None


class NoteResponse(NoteBase):
    id: int
    is_published: str
    voice_file_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class NoteListResponse(BaseModel):
    id: int
    title: str
    snippet: Optional[str]
    category: str
    tags: Optional[List[str]]
    read_time: int

    class Config:
        orm_mode = True
