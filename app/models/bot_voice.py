"""
Bot Voice model for storing custom audio files and trigger text
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base


class BotVoice(Base):
    __tablename__ = "bot_voices"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    trigger_text = Column(Text, nullable=False, index=True)  # Text that triggers this audio
    audio_url = Column(String(500), nullable=False)  # Path to uploaded audio file
    audio_filename = Column(String(255), nullable=False)  # Original filename
    priority = Column(Integer, default=5, index=True)  # Higher priority = more likely to be used
    is_active = Column(Boolean, default=True, index=True)
    duration_seconds = Column(Float, nullable=True)  # Audio duration
    file_size = Column(Integer, nullable=True)  # File size in bytes
    content_type = Column(String(100), default="audio/mpeg")  # MIME type
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), default="admin")  # Who uploaded this
    
    def __repr__(self):
        return f"<BotVoice(id={self.id}, title='{self.title}', priority={self.priority})>"
