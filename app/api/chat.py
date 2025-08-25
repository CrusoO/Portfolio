"""
Chat endpoints for AI assistant interaction
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat import ChatHistory
from app.schemas.chat import ChatMessage, ChatResponse, ChatHistoryResponse
from app.utils.ai_responses import get_ai_response

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def chat_with_cruso(message: ChatMessage, db: Session = Depends(get_db)):
    """Send message to Cruso AI assistant"""
    # Get AI response
    ai_response = get_ai_response(message.message, message.username)
    
    # Save to database
    chat_entry = ChatHistory(
        username=message.username,
        user_message=message.message,
        ai_response=ai_response
    )
    
    db.add(chat_entry)
    db.commit()
    
    return ChatResponse(response=ai_response, bot_name="Cruso")


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
