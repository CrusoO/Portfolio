#!/usr/bin/env python3
"""
Production deployment script for Robinson's Portfolio Backend
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met for deployment"""
    print("🔍 Checking deployment requirements...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and configure your environment variables.")
        return False
    
    # Check if database directory exists
    uploads_dir = Path("uploads/bot_audio")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Upload directories created")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    try:
        from app.core.database import create_tables
        create_tables()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_health_check():
    """Run basic health checks"""
    print("🩺 Running health checks...")
    try:
        # Import main app to check for import errors
        from app.main import app
        print("✅ Application imports successfully")
        
        # Check critical environment variables
        from app.core.config import settings
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            print("⚠️  WARNING: Using default SECRET_KEY! Change this in production!")
        
        print("✅ Health checks completed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting deployment process for Robinson's Portfolio Backend")
    print("=" * 60)
    
    steps = [
        ("Requirements Check", check_requirements),
        ("Install Dependencies", install_dependencies),
        ("Initialize Database", initialize_database),
        ("Health Check", run_health_check)
    ]
    
    for step_name, step_func in steps:
        print(f"
Step: {step_name}")
        if not step_func():
            print(f"❌ Deployment failed at step: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Deployment completed successfully!")
    print("🌐 Your backend is ready for production!")
    print("\n📋 Next steps:")
    print("   1. Start the server: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("   2. Visit: http://localhost:8000/docs for API documentation")
    print("   3. Health check: http://localhost:8000/health")

if __name__ == "__main__":
    main()
