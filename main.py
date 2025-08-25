"""
Quick Start FastAPI Backend for Robinson's Portfolio
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Cruso Portfolio Backend", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🚀 Cruso Portfolio Backend is Running!",
        "version": "1.0.0",
        "features": [
            "AI Chatbot (Cruso)",
            "Personal Notes API",
            "Paint Canvas Storage", 
            "Reviews System",
            "Contact Forms"
        ],
        "docs": "/docs"
    }

# Simple chatbot endpoint
@app.post("/api/chat/message")
async def chat(data: dict):
    user_message = data.get("message", "")
    username = data.get("username", "Anonymous")
    
    # Simple Cruso responses
    if "hi" in user_message.lower() or "hello" in user_message.lower():
        response = f"Hey {username}! 👋 I'm Cruso, Robinson's AI assistant. Want to try the paint canvas or learn about his projects?"
    elif "paint" in user_message.lower():
        response = "The paint canvas is awesome! 🎨 You can create digital art just like MS Paint. Give it a try!"
    elif "robinson" in user_message.lower():
        response = "Robinson is a Full-Stack Developer from Bangalore! He works with Vue.js, TypeScript, and FastAPI. Check out his projects!"
    elif "project" in user_message.lower():
        response = "Robinson has cool projects like CodeSensei (AI education) and AGRO_Frontend (agriculture). 🚀"
    else:
        response = f"That's interesting, {username}! I'm here to help you explore Robinson's portfolio. Try the paint canvas or check out his notes!"
    
    return {"response": response, "bot_name": "Cruso"}

# Notes endpoint
@app.get("/api/notes")
async def get_notes():
    return [
        {
            "id": 1,
            "title": "Square Peg, Round World",
            "category": "Identity",
            "snippet": "On being the odd one out in a world designed for everyone else...",
            "read_time": 6
        },
        {
            "id": 2, 
            "title": "The Man Who Collected Shadows",
            "category": "Story",
            "snippet": "A story about a peculiar man I met at the train station...",
            "read_time": 7
        }
    ]

# Reviews endpoint
@app.post("/api/reviews")
async def submit_review(data: dict):
    return {
        "message": "Review submitted successfully!",
        "review": data
    }

@app.get("/api/reviews/stats")
async def review_stats():
    return {
        "total_reviews": 12,
        "average_rating": 4.8,
        "rating_breakdown": {"5": 8, "4": 3, "3": 1}
    }

# Canvas endpoint
@app.post("/api/canvas/save")
async def save_artwork(data: dict):
    return {
        "message": "Artwork saved successfully!",
        "id": 123,
        "artist": data.get("username", "Anonymous")
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
