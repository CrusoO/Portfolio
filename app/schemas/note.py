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


class NoteResponse(NoteBase):
    id: int
    is_published: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    id: int
    title: str
    snippet: Optional[str]
    category: str
    tags: Optional[List[str]]
    read_time: int

    class Config:
        from_attributes = True
