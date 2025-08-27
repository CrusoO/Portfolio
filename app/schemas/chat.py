"""
Chat schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    username: Optional[str] = "Anonymous"
    with_voice: bool = False  # Request voice response
    voice_id: Optional[str] = None  # Custom voice ID


class ChatResponse(BaseModel):
    response: str
    bot_name: str = "Cruso"
    voice_audio: Optional[str] = None  # Base64 encoded audio if voice requested


class ChatHistoryResponse(BaseModel):
    id: int
    username: str
    user_message: str
    ai_response: str
    created_at: datetime
    
    class Config:
        orm_mode = True
