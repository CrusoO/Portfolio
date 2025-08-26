"""
Audio-related database models for caching and custom audio files
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AudioCache(Base):
    """
    Audio cache table for TTS generation caching
    Stores generated audio to avoid re-generating same text
    """
    __tablename__ = "audio_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    text_hash = Column(String(32), unique=True, index=True, nullable=False)  # MD5 hash
    voice_id = Column(String(100), default="default", nullable=False)
    voice_settings = Column(JSON, default={})
    audio_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float)  # Duration in seconds
    source = Column(String(20), default="generated")  # "generated" or "uploaded"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AudioCache(id={self.id}, text_hash='{self.text_hash}', voice_id='{self.voice_id}')>"


class CustomAudio(Base):
    """
    Custom audio files uploaded by admins for specific notes/content
    """
    __tablename__ = "custom_audio"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    audio_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float)  # Duration in seconds
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    text_content = Column(Text)  # Optional text content this audio represents
    is_active = Column(Boolean, default=True)
    
    # Timestamps  
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    note = relationship("Note", back_populates="custom_audio", foreign_keys=[note_id])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<CustomAudio(id={self.id}, title='{self.title}', note_id={self.note_id})>"
