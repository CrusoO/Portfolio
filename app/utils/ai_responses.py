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
    
    system_prompt = f"""You are Cruso, Robinson's AI assistant for his portfolio website. You help visitors explore his projects, skills, and work. Keep responses friendly, helpful, and focused on Robinson's portfolio. The user's name is {username}.

Robinson is a passionate full-stack developer who specializes in:
- Python, JavaScript, React, FastAPI
- AI/ML integration and modern web development
- Creating user-friendly solutions that combine technical expertise with creative problem-solving

His notable projects include:
- CodeSensei: An AI-powered education platform
- AGRO_Frontend: Agriculture management system
- This portfolio backend with AI chat integration

Keep responses concise (under 150 words), engaging, and always guide users to explore more of Robinson's work."""

    # Try Groq first (faster and often better)
    if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Fast and capable model
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
    
    # Predefined responses (fallback)
    if any(word in message_lower for word in ["hi", "hello", "hey"]):
        return f"Hey {username}! I'm Cruso, Robinson's AI assistant. How can I help you explore his portfolio?"
    
    elif any(word in message_lower for word in ["project", "projects", "work"]):
        return "Robinson has amazing projects like CodeSensei (AI education platform), AGRO_Frontend (agriculture management), and this portfolio backend! 🚀 Each showcases different skills in web development, AI integration, and user experience design."
    
    elif any(word in message_lower for word in ["skill", "skills", "technology", "tech"]):
        return "Robinson is skilled in Python, JavaScript, React, FastAPI, AI/ML, database design, and full-stack development. He loves creating solutions that combine modern web tech with AI capabilities! 💻"
    
    elif any(word in message_lower for word in ["paint", "canvas", "art", "draw"]):
        return "The paint canvas is one of my favorite features! You can create digital art just like MS Paint, and it saves your creations. Try it out and show off your artistic side! 🎨"
    
    elif any(word in message_lower for word in ["contact", "reach", "connect"]):
        return "You can reach Robinson through the contact form on his portfolio! He's always open to discussing new opportunities, collaborations, or just chatting about technology. 📧"
    
    elif any(word in message_lower for word in ["about", "who", "robinson"]):
        return "Robinson is a passionate full-stack developer who loves creating innovative web applications. He combines technical expertise with creative problem-solving to build user-friendly solutions! 👨‍💻"
    
    else:
        return f"That's interesting, {username}! I'm here to help you explore Robinson's work and skills. Feel free to ask me about his projects, skills, or use the interactive features like the paint canvas!"
