"""
Core configuration settings for the FastAPI application
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Robinson's Portfolio Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS settings
    CORS_ORIGINS: str = "*"  # Can be comma-separated list
    
    # AI Integration settings (optional)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "groq"  # "groq", "openai", or "fallback"
    
    # ElevenLabs TTS settings
    ELEVENLABS_API_KEY: Optional[str] = None
    DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default ElevenLabs voice)
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    AUDIO_DIR: str = "storage/audio"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_TYPES: list = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a", "audio/ogg"]
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
