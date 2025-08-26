"""
Note model for blog posts and articles
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    snippet = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False, default="General")
    tags = Column(JSON, nullable=True)  # List of tags as JSON
    read_time = Column(Integer, nullable=False, default=5)  # in minutes
    is_published = Column(String(10), nullable=False, default="draft")  # draft, published, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    custom_audio = relationship("CustomAudio", back_populates="note", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', category='{self.category}')>"
