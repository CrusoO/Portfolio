"""
Voice endpoints for text-to-speech and voice note functionality
"""
import os
import io
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from elevenlabs import generate, set_api_key, Voice, VoiceSettings
import base64

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_admin_user
from app.models.user import User

router = APIRouter(prefix="/api/voice", tags=["Voice"])


class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75
    style: Optional[float] = 0.0
    use_speaker_boost: Optional[bool] = True


class VoiceResponse(BaseModel):
    success: bool
    audio_base64: Optional[str] = None
    message: str


@router.post("/text-to-speech", response_model=VoiceResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech using ElevenLabs API"""
    
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY environment variable."
        )
    
    try:
        # Set the API key
        set_api_key(settings.ELEVENLABS_API_KEY)
        
        # Use provided voice_id or default
        voice_id = request.voice_id or settings.ELEVENLABS_VOICE_ID
        
        # Create voice settings
        voice_settings = VoiceSettings(
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=request.use_speaker_boost
        )
        
        # Generate audio
        audio = generate(
            text=request.text,
            voice=Voice(voice_id=voice_id, settings=voice_settings),
            model="eleven_multilingual_v2"
        )
        
        # Convert audio to base64
        audio_base64 = base64.b64encode(audio).decode('utf-8')
        
        return VoiceResponse(
            success=True,
            audio_base64=audio_base64,
            message="Audio generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audio: {str(e)}"
        )


@router.post("/text-to-speech/stream")
async def text_to_speech_stream(request: TextToSpeechRequest):
    """Convert text to speech and return as audio stream"""
    
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="ElevenLabs API key not configured"
        )
    
    try:
        set_api_key(settings.ELEVENLABS_API_KEY)
        
        voice_id = request.voice_id or settings.ELEVENLABS_VOICE_ID
        
        voice_settings = VoiceSettings(
            stability=request.stability,
            similarity_boost=request.similarity_boost,
            style=request.style,
            use_speaker_boost=request.use_speaker_boost
        )
        
        audio = generate(
            text=request.text,
            voice=Voice(voice_id=voice_id, settings=voice_settings),
            model="eleven_multilingual_v2"
        )
        
        # Create audio stream
        audio_stream = io.BytesIO(audio)
        
        return StreamingResponse(
            io.BytesIO(audio),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate audio stream: {str(e)}"
        )


@router.get("/voices")
async def get_available_voices():
    """Get list of available ElevenLabs voices"""
    
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=400, 
            detail="ElevenLabs API key not configured"
        )
    
    try:
        set_api_key(settings.ELEVENLABS_API_KEY)
        from elevenlabs import voices
        
        available_voices = voices()
        
        voice_list = []
        for voice in available_voices:
            voice_list.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "description": getattr(voice, 'description', 'No description available')
            })
        
        return {
            "success": True,
            "voices": voice_list,
            "total": len(voice_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch voices: {str(e)}"
        )


@router.get("/test")
async def test_voice_api():
    """Test endpoint to check ElevenLabs API connectivity"""
    
    if not settings.ELEVENLABS_API_KEY:
        return {
            "configured": False,
            "message": "ElevenLabs API key not set",
            "instructions": "Set ELEVENLABS_API_KEY environment variable"
        }
    
    try:
        set_api_key(settings.ELEVENLABS_API_KEY)
        
        # Test with a short text
        audio = generate(
            text="Hello, this is a test.",
            voice=Voice(voice_id=settings.ELEVENLABS_VOICE_ID),
            model="eleven_multilingual_v2"
        )
        
        return {
            "configured": True,
            "message": "ElevenLabs API is working correctly",
            "voice_id": settings.ELEVENLABS_VOICE_ID,
            "audio_size": len(audio)
        }
        
    except Exception as e:
        return {
            "configured": False,
            "message": f"ElevenLabs API error: {str(e)}",
            "error": str(e)
        }
