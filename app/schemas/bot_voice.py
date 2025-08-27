"""
Pydantic schemas for Bot Voice audio functionality
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class BotVoiceSearchRequest(BaseModel):
    searchText: str = Field(..., min_length=1, max_length=500, description="Text to search for matching audio")
    limit: Optional[int] = Field(default=10, ge=1, le=50, description="Maximum number of results")
    min_priority: Optional[int] = Field(default=1, ge=1, le=10, description="Minimum priority level")


class BotVoiceSearchResult(BaseModel):
    id: int
    title: str
    audio_url: str
    trigger_text: str
    priority: int
    duration_seconds: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BotVoiceSearchResponse(BaseModel):
    success: bool
    results: List[BotVoiceSearchResult]
    total_found: int
    search_text: str


class BotVoiceUploadRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    trigger_text: str = Field(..., min_length=1, max_length=1000, description="Text that triggers this audio")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Priority level (1-10)")
    is_active: Optional[bool] = Field(True)


class BotVoiceUploadResponse(BaseModel):
    success: bool
    message: str
    bot_voice_id: Optional[int] = None
    audio_url: Optional[str] = None


class BotVoiceListResponse(BaseModel):
    success: bool
    bot_voices: List[BotVoiceSearchResult]
    total: int


class BotVoiceUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    trigger_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class BotVoiceDeleteResponse(BaseModel):
    success: bool
    message: str
