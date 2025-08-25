"""
Alternative entry point for running the application
Useful for development and testing
"""
import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Get port from environment (for deployment platforms like Render)
    port = int(os.environ.get("PORT", settings.PORT))
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG,
        access_log=settings.DEBUG
    )
