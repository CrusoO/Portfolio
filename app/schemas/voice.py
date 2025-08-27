"""
Voice-related schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional


class VoiceNoteCreate(BaseModel):
    note_id: int
    voice_text: str  # Text to convert to speech
    voice_id: Optional[str] = None
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75
    style: Optional[float] = 0.0
    use_speaker_boost: Optional[bool] = True


class VoiceNoteResponse(BaseModel):
    success: bool
    message: str
    note_id: int
    voice_file_path: Optional[str] = None
    voice_duration: Optional[int] = None


class VoiceNoteUpdate(BaseModel):
    voice_text: Optional[str] = None
    voice_id: Optional[str] = None
    stability: Optional[float] = None
    similarity_boost: Optional[float] = None
    style: Optional[float] = None
    use_speaker_boost: Optional[bool] = None
