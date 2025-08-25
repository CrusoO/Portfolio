#!/usr/bin/env python3
"""
Quick setup script for Robinson's Portfolio Backend
"""
import os
import shutil
import subprocess
import sys


def create_env_file():
    """Create .env file from example with Groq API key"""
    if os.path.exists('.env'):
        print("  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            return
    
    # Copy from example
    if os.path.exists('.env.example'):
        shutil.copy('.env.example', '.env')
        print(" Created .env file from .env.example")
        
        # Update with Groq API key
        with open('.env', 'r') as f:
            content = f.read()
        
        # Prompt user for Groq API key
        groq_key = input("Enter your Groq API key: ").strip()
        if groq_key:
            content = content.replace('GROQ_API_KEY=""', f'GROQ_API_KEY="{groq_key}"')
        content = content.replace('DEBUG=False', 'DEBUG=True')
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print(" Configured with your Groq API key for lightning-fast AI responses!")
    else:
        print(" .env.example not found")


def install_dependencies():
    """Install Python dependencies"""
    print(" Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print(" Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print(" Failed to install dependencies")
        return False
    return True


def initialize_database():
    """Initialize the database"""
    print(" Initializing database...")
    try:
        subprocess.check_call([sys.executable, 'scripts/init_db.py'])
        print(" Database initialized successfully!")
    except subprocess.CalledProcessError:
        print(" Failed to initialize database")
        return False
    return True


def main():
    """Main setup function"""
    print(" Setting up Robinson's Portfolio Backend")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('requirements.txt'):
        print(" Please run this script from the project root directory")
        return 1
    
    steps = [
        ("Creating environment file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Initializing database", initialize_database)
    ]
    
    for step_name, step_func in steps:
        print(f"\n {step_name}...")
        if step_func and not step_func():
            print(f" Setup failed at step: {step_name}")
            return 1
    
    print("\n Setup completed successfully!")
    print("\n Ready to run:")
    print("   python run.py")
    print("\n Then visit:")
    print("   http://localhost:8000 - API info")
    print("   http://localhost:8000/docs - Interactive documentation")
    
    print("\n Your AI assistant 'Cruso' is powered by Groq for super-fast responses!")
    
    return 0


if __name__ == "__main__":
    exit(main())
