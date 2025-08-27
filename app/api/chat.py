"""
Chat endpoints for AI assistant interaction
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from elevenlabs import generate, set_api_key, Voice, VoiceSettings
import base64

from app.core.database import get_db
from app.core.config import settings
from app.models.chat import ChatHistory
from app.schemas.chat import ChatMessage, ChatResponse, ChatHistoryResponse
from app.utils.ai_responses import get_ai_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def chat_with_cruso(message: ChatMessage, db: Session = Depends(get_db)):
    """Send message to Cruso AI assistant with optional voice response"""
    # Get AI response
    ai_response = get_ai_response(message.message, message.username)
    
    # Initialize response object
    response_data = ChatResponse(response=ai_response, bot_name="Cruso")
    
    # Generate voice if requested
    if message.with_voice and settings.ELEVENLABS_API_KEY:
        try:
            set_api_key(settings.ELEVENLABS_API_KEY)
            
            voice_id = message.voice_id or settings.ELEVENLABS_VOICE_ID
            
            # Generate audio
            audio = generate(
                text=ai_response,
                voice=Voice(voice_id=voice_id),
                model="eleven_multilingual_v2"
            )
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio).decode('utf-8')
            response_data.voice_audio = audio_base64
            
        except Exception as e:
            print(f"Voice generation failed: {e}")
            # Don't fail the whole request if voice fails
    
    # Save to database
    chat_entry = ChatHistory(
        username=message.username,
        user_message=message.message,
        ai_response=ai_response
    )
    
    db.add(chat_entry)
    db.commit()
    
    return response_data


@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent chat history"""
    history = db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    return history


@router.delete("/history")
async def clear_chat_history(db: Session = Depends(get_db)):
    """Clear all chat history"""
    db.query(ChatHistory).delete()
    db.commit()
    return {"message": "Chat history cleared successfully"}
