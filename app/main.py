"""
FastAPI application entry point for Robinson's Portfolio Backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import uvicorn

from app.core.config import settings
from app.core.database import create_tables
from app.api import auth, chat, reviews, contact, canvas, notes, audio

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive backend API for Robinson's portfolio website",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Audio file serving
if not os.path.exists(settings.AUDIO_DIR):
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
app.mount("/storage/audio", StaticFiles(directory=settings.AUDIO_DIR), name="audio")

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(reviews.router)
app.include_router(contact.router)
app.include_router(canvas.router)
app.include_router(notes.router)
app.include_router(audio.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_tables()


@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
    """Handle internal server errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 Robinson's Portfolio Backend API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "authentication": {
                "register": "/auth/register",
                "login": "/auth/login"
            },
            "chat": {
                "message": "/api/chat/message",
                "history": "/api/chat/history"
            },
            "notes": {
                "list": "/api/notes",
                "detail": "/api/notes/{id}"
            },
            "reviews": {
                "submit": "/api/reviews",
                "list": "/api/reviews",
                "stats": "/api/reviews/stats"
            },
            "contact": {
                "submit": "/api/contact/submit",
                "list": "/api/contact"
            },
            "canvas": {
                "save": "/api/canvas/save",
                "list": "/api/canvas",
                "detail": "/api/canvas/{id}"
            },
            "audio": {
                "tts": "/api/audio/tts",
                "cache": "/api/audio/cache/{text_hash}",
                "cache_stats": "/api/audio/cache/stats",
                "cache_cleanup": "/api/audio/cache/cleanup",
                "upload_custom": "/api/audio/custom",
                "list_custom": "/api/audio/custom",
                "search_custom": "/api/audio/custom/search"
            }
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
