"""
Chat schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    username: Optional[str] = "Anonymous"


class ChatResponse(BaseModel):
    response: str
    bot_name: str = "Cruso"


class ChatHistoryResponse(BaseModel):
    id: int
    username: str
    user_message: str
    ai_response: str
    created_at: datetime
    
    class Config:
        from_attributes = True
