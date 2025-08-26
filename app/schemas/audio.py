"""
Pydantic schemas for audio-related operations
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Audio Cache Schemas
class AudioCacheBase(BaseModel):
    text: str = Field(..., description="Text content for TTS generation")
    voice_id: str = Field(default="default", description="Voice ID for TTS")
    voice_settings: Optional[Dict[str, Any]] = Field(default={}, description="Voice settings")


class AudioCacheCreate(AudioCacheBase):
    pass


class AudioCacheResponse(AudioCacheBase):
    id: int
    text_hash: str
    audio_url: str
    file_name: str
    file_size: int
    duration: Optional[float] = None
    source: str
    created_at: datetime
    last_used: datetime
    
    class Config:
        from_attributes = True


# Custom Audio Schemas
class CustomAudioBase(BaseModel):
    title: str = Field(..., description="Title of the custom audio")
    description: Optional[str] = Field(None, description="Description of the audio")
    text_content: Optional[str] = Field(None, description="Text content this audio represents")


class CustomAudioCreate(CustomAudioBase):
    note_id: Optional[int] = Field(None, description="Associated note ID")


class CustomAudioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    text_content: Optional[str] = None
    is_active: Optional[bool] = None


class CustomAudioResponse(CustomAudioBase):
    id: int
    note_id: Optional[int] = None
    audio_url: str
    file_name: str
    file_size: int
    duration: Optional[float] = None
    uploaded_by: Optional[int] = None
    is_active: bool
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# TTS Request Schema
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to convert to speech")
    voice_id: Optional[str] = Field(default="default", description="Voice ID to use")
    voice_settings: Optional[Dict[str, Any]] = Field(default={}, description="Voice settings")
    use_cache: bool = Field(default=True, description="Whether to use cache")


class TTSResponse(BaseModel):
    audio_url: str
    text_hash: str
    cached: bool
    file_size: int
    duration: Optional[float] = None
    voice_id: str


# Audio Search Schema
class AudioSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    search_type: str = Field(default="all", description="Type of search: 'title', 'description', 'content', 'all'")


# Cache Statistics Schema
class CacheStatsResponse(BaseModel):
    total_cached: int
    total_size_bytes: int
    unique_voices: int
    oldest_entry: Optional[datetime] = None
    newest_entry: Optional[datetime] = None
    cache_hit_rate: Optional[float] = None
    used_last_week: int
