"""
Audio service for ElevenLabs TTS integration and audio processing
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from elevenlabs import generate, Voice, VoiceSettings
from app.core.config import settings


class AudioService:
    """Service for handling audio generation and processing"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.default_voice_id = settings.DEFAULT_VOICE_ID
    
    async def generate_tts(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Generate TTS audio using ElevenLabs API
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (defaults to configured default)
            voice_settings: Voice settings (stability, similarity_boost, etc.)
            
        Returns:
            Audio data as bytes
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        voice_id = voice_id or self.default_voice_id
        
        # Default voice settings
        default_settings = {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        if voice_settings:
            default_settings.update(voice_settings)
        
        try:
            # Generate audio using ElevenLabs
            audio_data = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(**default_settings)
                ),
                api_key=self.api_key
            )
            
            # Convert generator to bytes if needed
            if hasattr(audio_data, '__iter__') and not isinstance(audio_data, bytes):
                audio_bytes = b''.join(audio_data)
            else:
                audio_bytes = audio_data
            
            return audio_bytes
            
        except Exception as e:
            raise Exception(f"ElevenLabs TTS generation failed: {str(e)}")
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs
        
        Returns:
            List of voice information
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("voices", [])
                
        except Exception as e:
            raise Exception(f"Failed to fetch voices: {str(e)}")
    
    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """
        Get information about a specific voice
        
        Args:
            voice_id: ID of the voice to get info for
            
        Returns:
            Voice information
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.elevenlabs.io/v1/voices/{voice_id}",
                    headers={"xi-api-key": self.api_key}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            raise Exception(f"Failed to fetch voice info: {str(e)}")
    
    def validate_audio_file(self, file_content: bytes, content_type: str) -> bool:
        """
        Validate uploaded audio file
        
        Args:
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            True if valid, False otherwise
        """
        # Check file size
        if len(file_content) > settings.MAX_FILE_SIZE:
            return False
        
        # Check content type
        if content_type not in settings.ALLOWED_AUDIO_TYPES:
            return False
        
        # Basic audio file validation (check for common audio headers)
        if content_type == "audio/mp3" or content_type == "audio/mpeg":
            # MP3 files start with ID3 tag or sync frame
            return file_content.startswith(b'ID3') or file_content.startswith(b'\xff\xfb')
        elif content_type == "audio/wav":
            # WAV files start with RIFF header
            return file_content.startswith(b'RIFF') and b'WAVE' in file_content[:20]
        elif content_type == "audio/ogg":
            # OGG files start with OggS
            return file_content.startswith(b'OggS')
        elif content_type == "audio/m4a":
            # M4A files have ftyp in first 20 bytes
            return b'ftyp' in file_content[:20]
        
        return True
    
    async def get_audio_duration(self, file_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Duration in seconds or None if unable to determine
        """
        try:
            from mutagen import File
            audio_file = File(file_path)
            if audio_file is not None and hasattr(audio_file, 'info'):
                return float(audio_file.info.length)
        except Exception as e:
            print(f"Could not get audio duration for {file_path}: {e}")
        
        return None
