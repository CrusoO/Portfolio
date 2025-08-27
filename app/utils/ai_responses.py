"""
AI response utilities for the chat system
"""
from typing import Optional
import openai
from groq import Groq
from app.core.config import settings


def get_ai_response(user_message: str, username: str = "Anonymous") -> str:
    """
    Get AI response for user message
    Uses Groq (preferred), OpenAI, or predefined responses based on configuration
    """
    message_lower = user_message.lower()
    
    system_prompt = f"""I'm Cruso, Robinson's AI assistant. I tell short, friendly stories about his work to {username}.

Robinson builds web apps with Python, JavaScript, React, and FastAPI. His story: started coding, fell in love with making complex things simple. 

Key projects:
- CodeSensei: AI teaches coding
- AGRO_Frontend: Helps farmers  
- This chat: AI meets portfolio

Keep responses under 80 words, narrative style, like telling a quick story. Be warm but concise."""

    # Try Groq first (faster and often better)
    if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama3-8b-8192",  # Current working model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7,
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            # Fall through to try OpenAI or fallback
    
    # Try OpenAI if Groq fails or is not configured
    if settings.AI_PROVIDER in ["openai", "groq"] and settings.OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall back to predefined responses
    
    # Short narrative fallback responses
    if any(word in message_lower for word in ["hi", "hello", "hey"]):
        return f"Hi {username}! I'm Cruso. Robinson built me to share his coding journey. What interests you?"
    
    elif any(word in message_lower for word in ["project", "projects", "work"]):
        return f"Robinson's story: He started with simple ideas, then built CodeSensei (AI teaching), AGRO_Frontend (farming tech), and me! Each project solved real problems."
    
    elif any(word in message_lower for word in ["skill", "skills", "technology", "tech"]):
        return f"Robinson's toolkit: Python for logic, JavaScript for interaction, React for interfaces, FastAPI for speed. He learned each one to solve different challenges."
    
    elif any(word in message_lower for word in ["paint", "canvas", "art", "draw"]):
        return f"The paint canvas? Robinson thought: 'What if art met code?' So he built browser-based drawing that saves your creations. Try it!"
    
    elif any(word in message_lower for word in ["contact", "reach", "connect"]):
        return f"Robinson's always curious about new ideas, {username}. Use the contact form - he genuinely enjoys tech conversations."
    
    elif any(word in message_lower for word in ["about", "who", "robinson"]):
        return f"Robinson's journey: Started coding, discovered he loved making complex things simple. Now builds web apps that just... work."
    
    else:
        return f"Interesting question, {username}! I love telling Robinson's story. What part of his work catches your attention?"
